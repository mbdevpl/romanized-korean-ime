"""Setup script."""

import setup_boilerplate


class Package(setup_boilerplate.Package):

    """Package metadata."""

    name = 'romanized-korean-ime'
    description = 'romanized Korean Input Method Editor (IME) - type latin script, get hangul'
    download_url = 'https://github.com/mbdevpl/romanized-korean-ime'
    classifiers = [
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only']
    keywords = ['korean', 'ime', 'hangul', 'jamo']


if __name__ == '__main__':
    Package.setup()
