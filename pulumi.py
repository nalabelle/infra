"""A Python Pulumi program"""

import pulumi
import pulumi_tailscale as tailscale

gibson = tailscale.DeviceTags(
    "gibson",
    device_id="1476909196181687",
    tags=["tag:servers"],
    opts=pulumi.ResourceOptions(protect=True),
)

acl = tailscale.Acl(
    "acl",
    acl="""// Example/default ACLs for unrestricted connections.
{
\x09// Declare static groups of users. Use autogroups for all users or users with a specific role.
\x09// "groups": {
\x09//  \x09"group:example": ["alice@example.com", "bob@example.com"],
\x09// },

\x09// Define the tags which can be applied to devices and by which users.
\x09"tagOwners": {
\x09\x09"tag:servers": ["autogroup:admin"],
\x09},

\x09// Define access control lists for users, groups, autogroups, tags,
\x09// Tailscale IP addresses, and subnet ranges.
\x09"acls": [
\x09\x09// Allow all connections.
\x09\x09// Comment this section out if you want to define specific restrictions.
\x09\x09{"action": "accept", "src": ["*"], "dst": ["*:*"]},

\x09\x09// Allow users in "group:example" to access "tag:example", but only from
\x09\x09// devices that are running macOS and have enabled Tailscale client auto-updating.
\x09\x09// {"action": "accept", "src": ["group:example"], "dst": ["tag:example:*"], "srcPosture":["posture:autoUpdateMac"]},
\x09],

\x09// Define postures that will be applied to all rules without any specific
\x09// srcPosture definition.
\x09// "defaultSrcPosture": [
\x09//      "posture:anyMac",
\x09// ],

\x09// Define device posture rules requiring devices to meet
\x09// certain criteria to access parts of your system.
\x09// "postures": {
\x09//      // Require devices running macOS, a stable Tailscale
\x09//      // version and auto update enabled for Tailscale.
\x09// \x09"posture:autoUpdateMac": [
\x09// \x09    "node:os == 'macos'",
\x09// \x09    "node:tsReleaseTrack == 'stable'",
\x09// \x09    "node:tsAutoUpdate",
\x09// \x09],
\x09//      // Require devices running macOS and a stable
\x09//      // Tailscale version.
\x09// \x09"posture:anyMac": [
\x09// \x09    "node:os == 'macos'",
\x09// \x09    "node:tsReleaseTrack == 'stable'",
\x09// \x09],
\x09// },

\x09// Define users and devices that can use Tailscale SSH.
\x09"ssh": [
\x09\x09// Allow all users to SSH into their own devices in check mode.
\x09\x09// Comment this section out if you want to define specific restrictions.
\x09\x09{
\x09\x09\x09"action": "check",
\x09\x09\x09"src":    ["autogroup:member"],
\x09\x09\x09"dst":    ["autogroup:self"],
\x09\x09\x09"users":  ["autogroup:nonroot", "root"],
\x09\x09},
\x09],

\x09// Test access rules every time they're saved.
\x09// "tests": [
\x09//  \x09{
\x09//  \x09\x09"src": "alice@example.com",
\x09//  \x09\x09"accept": ["tag:example"],
\x09//  \x09\x09"deny": ["100.101.102.103:443"],
\x09//  \x09},
\x09// ],
}
""",
    opts=pulumi.ResourceOptions(protect=True),
)
