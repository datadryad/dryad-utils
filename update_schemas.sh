#!/usr/bin/env bash

echo "Installing metadata schemas"
/opt/dryad/bin/dsrun org.dspace.administer.MetadataImporter -f /opt/dryad/config/registries/dryad-types.xml
/opt/dryad/bin/dsrun org.dspace.administer.MetadataImporter -f /opt/dryad/config/registries/workflow-types.xml
/opt/dryad/bin/dsrun org.dspace.administer.MetadataImporter -f /opt/dryad/config/registries/internal-types.xml
/opt/dryad/bin/dsrun org.dspace.administer.MetadataImporter -f /opt/dryad/config/registries/prism-types.xml
/opt/dryad/bin/dsrun org.dspace.administer.MetadataImporter -f /opt/dryad/config/registries/journal-types.xml
