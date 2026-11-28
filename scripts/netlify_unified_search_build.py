"""Compatibility entry point for existing Netlify deployments.

The same provider-neutral build is used for Cloudflare preview qualification.
"""
from .build_public_site import main

if __name__ == "__main__":
    main()
