#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

changelog_file=CHANGELOG

if [ ! -f "$changelog_file" ]; then
    echo "CHANGELOG file not found."
    exit 1
fi

version=$1
package="das-cli"
date=$(date -R)
maintainer_name="Rafael Levi"
maintainer_email="rafael.levi@singularitynet.io"

changelog="${package} (${version}) stable; urgency=medium\n\n"

changelog+=$(sed -n '1,$p' $changelog_file | sed 's/^\[#.*\] //')

changelog="${changelog}\n\n -- ${maintainer_name} <${maintainer_email}>  ${date}\n"

echo -e "$changelog" >debian/changelog
