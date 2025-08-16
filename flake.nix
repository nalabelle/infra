{
  description = "Infrastructure development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };

        # Python packages from devbox.json
        pythonEnv = pkgs.python313.withPackages (ps: [
          # Add any Python packages here if needed
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Core tools
            ansible
            ansible-lint
            pre-commit
            shellcheck
            shfmt
            gnumake
            _1password-cli
            vendir
            nodePackages.prettier
            uv
            python313

            # Python environment
            pythonEnv
          ];

          shellHook = ''
            # Activate virtual environment if it exists (similar to devbox init_hook)
            if [ -d ".venv" ]; then
              echo "Activating virtual environment..."
              source .venv/bin/activate
            fi

            echo "Development environment ready!"
            echo "Available tools:"
            echo "  - ansible: $(ansible --version | head -n1)"
            echo "  - ansible-lint: $(ansible-lint --version | head -n1)"
            echo "  - pre-commit: $(pre-commit --version)"
            echo "  - shellcheck: $(shellcheck --version | head -n1)"
            echo "  - shfmt: $(shfmt --version)"
            echo "  - make: $(make --version | head -n1)"
            echo "  - op: $(op --version)"
            echo "  - vendir: $(vendir version)"
            echo "  - prettier: $(prettier --version)"
            echo "  - uv: $(uv --version)"
            echo "  - python: $(python --version)"
          '';
        };
      });
}
