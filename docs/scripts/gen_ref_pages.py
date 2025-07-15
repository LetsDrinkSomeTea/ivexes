"""Generate the code reference pages and navigation."""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

src_root = Path(__file__).parent.parent.parent / 'src'

for path in sorted(src_root.rglob('*.py')):
    module_path = path.relative_to(src_root).with_suffix('')
    doc_path = path.relative_to(src_root).with_suffix('.md')
    full_doc_path = Path('api') / doc_path

    parts = tuple(module_path.parts)

    if parts[-1] == '__init__':
        parts = parts[:-1]
        doc_path = doc_path.with_name('index.md')
        full_doc_path = full_doc_path.with_name('index.md')
    elif parts[-1] == '__main__':
        continue

    # Skip if no actual module name
    if not parts:
        continue

    # Create navigation entry
    nav[parts] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, 'w') as fd:
        ident = '.'.join(parts)

        # Generate page header
        print(f'# {ident}', file=fd)
        print('', file=fd)

        # Add module docstring reference
        print(f'::: {ident}', file=fd)
        print('    options:', file=fd)
        print('      show_root_heading: false', file=fd)
        print('      show_root_toc_entry: false', file=fd)
        print('      heading_level: 2', file=fd)

    mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(src_root.parent))

with mkdocs_gen_files.open('api/SUMMARY.md', 'w') as nav_file:
    nav_file.writelines(nav.build_literate_nav())
