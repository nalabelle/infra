import logging
from dataclasses import dataclass

import requests
from lib.nextdns_config import NextDNSConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

nUrlLogin = "https://api.nextdns.io/accounts/@login"
nUrlSet = "https://api.nextdns.io/profiles/{nextDNSId}/rewrites"
nUrlDel = "https://api.nextdns.io/profiles/{nextDNSId}/rewrites/{rId}"
nHeaders = {"Origin": "https://my.nextdns.io"}


@dataclass
class Rewrite:
    id: str
    name: str
    type: str
    content: str
    seen: bool = False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rewrite):
            return False
        return self.name == other.name and self.type == other.type and self.content == other.content

    @staticmethod
    def from_json(jsonValue: dict[str, str]) -> "Rewrite":
        return Rewrite(jsonValue["id"], jsonValue["name"], jsonValue["type"], jsonValue["content"])


class Tracker:
    def __init__(
        self,
        config: NextDNSConfig,
    ) -> None:
        self.session: requests.Session = requests.Session()  # Initialize first
        self.session = self._login(config.email, config.password)  # Then login
        self.nextdns_id = config.id
        self.rewrites = self.get_rewrites()

    def _login(
        self,
        email: str,
        password: str,
    ) -> requests.Session:
        if hasattr(self.session, "cookies") and len(self.session.cookies) > 0:
            return self.session
        session = requests.Session()
        nextDNSCreds = {"email": email, "password": password}
        reqLogin = session.post(nUrlLogin, json=nextDNSCreds, headers=nHeaders)
        logger.debug("Login response: %s", reqLogin.text)
        if reqLogin.status_code != 200:
            raise Exception("Error: " + reqLogin.text)
        return session

    def update_rewrites(self, rewrites: list[Rewrite] | None = None) -> None:
        if not rewrites:
            rewrites = self.read_rewrites_from_file()
        for rewrite in rewrites:
            possible_matches = [r for r in self.rewrites if r.name == rewrite.name]
            if possible_matches:
                matched_rewrite: Rewrite | None = None
                if rewrite.type == "CNAME":
                    cname_matches = [r for r in possible_matches if r.type == "CNAME"]
                    if cname_matches:
                        matched_rewrite = cname_matches[0]
                elif rewrite.type == "AAAA":
                    aaaa_matches = [r for r in possible_matches if r.type == "AAAA"]
                    if aaaa_matches:
                        matched_rewrite = aaaa_matches[0]
                else:
                    # IPv4
                    a_matches = [r for r in possible_matches if r.type == "A"]
                    if a_matches:
                        matched_rewrite = a_matches[0]
                if not matched_rewrite or matched_rewrite.content != rewrite.content:
                    logger.info(f"Updating rewrite for {rewrite.name} ({rewrite.type})")
                    self.create_rewrite(rewrite)
                else:
                    matched_rewrite.seen = True
            else:
                logger.info(f"Creating rewrite for {rewrite.name} ({rewrite.type})")
                self.create_rewrite(rewrite)
        unseen = [rewrite for rewrite in self.rewrites if not rewrite.seen]
        for rewrite in unseen:
            self.delete_rewrite_by_id(rewrite.id)

    def get_rewrites(self) -> list[Rewrite]:
        reqRewrites = self.session.get(nUrlSet.format(nextDNSId=self.nextdns_id), headers=nHeaders)
        logger.debug("Get rewrites response: %s", reqRewrites.text)
        try:
            jsonValue = reqRewrites.json()
            if "data" not in jsonValue:
                raise ValueError(f"Unexpected API response format: {jsonValue}")
            return [Rewrite.from_json(rewrite) for rewrite in jsonValue["data"]]
        except Exception as e:
            logger.error("Failed to parse rewrites response: %s", e)
            raise

    def delete_rewrite_by_id(self, rewrite_id: str) -> None:
        my_rewrites = [r for r in self.rewrites if r.id == rewrite_id]
        if my_rewrites:
            logger.info(
                "Deleting rewrite %s, type %s, %s -> %s",
                my_rewrites[0].id,
                my_rewrites[0].type,
                my_rewrites[0].name,
                my_rewrites[0].content,
            )
        else:
            logger.info("Deleting rewrite %s (not in db)", rewrite_id)
        result = self.session.delete(nUrlDel.format(nextDNSId=self.nextdns_id, rId=rewrite_id), headers=nHeaders)
        for rewrite in my_rewrites:
            self.rewrites.remove(rewrite)
        if "errors" in result.text:
            raise Exception("Error: " + result.text)

    def delete_rewrite(self, name: str) -> None:
        to_delete = [rewrite.id for rewrite in self.rewrites if rewrite.name == name]
        for rewriteId in to_delete:
            self.delete_rewrite_by_id(rewriteId)

    def create_rewrite(self, host: Rewrite) -> None:
        reqCreate = self.session.post(
            nUrlSet.format(nextDNSId=self.nextdns_id),
            json={"name": host.name, "content": host.content},
            headers=nHeaders,
        )
        logger.debug("Create rewrite response: %s", reqCreate.text)
        results = reqCreate.json()
        if "errors" in reqCreate.text:
            if results["errors"][0]:
                error = results["errors"][0]
                if error["code"] == "conflict" and error["source"]["pointer"] == "name":
                    logger.debug(f"Error: {reqCreate.text}")
                    self.delete_rewrite(host.name)
                    return self.create_rewrite(host)
            else:
                raise Exception("Error: " + reqCreate.text)
        logger.info(
            "Updated %s record for %s -> %s",
            results["data"]["type"],
            results["data"]["name"],
            results["data"]["content"],
        )

    def read_rewrites_from_file(self, file_path: str | None = None, content: str | None = None) -> list[Rewrite]:
        """Read and parse rewrites from file or content string.

        Args:
            file_path: Path to file containing rewrite rules
            content: String containing rewrite rules

        Returns:
            List of parsed Rewrite objects

        Raises:
            ValueError: If neither file_path nor content provided
                      If invalid IP format encountered
        """
        """
        Read rewrites from a file.

        Args:
            file_path: Path to the file containing rewrites
            content: Content to parse instead of reading from file

        Returns:
            List[Rewrite]: List of rewrites
        """
        rewrites = []

        if file_path is None and content is None:
            raise ValueError("Either file_path or content must be provided")
        elif content is not None:
            lines = content.splitlines()
        else:
            # At this point, file_path cannot be None due to the check above
            assert file_path is not None
            with open(file_path) as f:
                lines = f.readlines()

        logger.info("Processing %s rewrites", len(lines))
        for line in lines:
            # Skip empty lines and comments
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Split the line and remove whitespace
            parts = [part.strip() for part in line.split()]
            if len(parts) == 2:
                ip, hostname = parts
                # Determine record type based on IP format
                # Determine record type based on IP address format
                if ":" in ip:
                    # IPv6 addresses contain colons
                    record_type = "AAAA"
                elif all(part.isdigit() for part in ip.split(".")):
                    # IPv4 addresses are dot-separated numbers
                    record_type = "A"
                else:
                    # Assume it's a hostname/CNAME if not IPv4 or IPv6
                    record_type = "CNAME"
                if record_type is None:
                    raise ValueError(f"Invalid IP format: {line}")
                rewrites.append(
                    Rewrite(
                        id="",  # ID will be set when created in NextDNS
                        name=hostname,
                        type=record_type,
                        content=ip,
                        seen=False,
                    )
                )
        return rewrites
