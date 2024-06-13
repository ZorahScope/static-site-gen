import pathlib
import shutil


def copy_static_dir_to_public() -> None:
    # define source and destination directories
    public_dir_path = pathlib.Path("../public")
    static_dir_path = pathlib.Path("../static")
    # delete public folder and recreate an empty one
    print(f"Deleting folder: {public_dir_path}")
    shutil.rmtree(public_dir_path, ignore_errors=True)
    print(f"Creating folder: {static_dir_path}")
    public_dir_path.mkdir()

    static_dir_contents = list(static_dir_path.rglob('*'))
    src_dst_list = []
    # create destination paths from source directory
    for path in static_dir_contents:
        src_dst_list.append(
            (path,
             public_dir_path / path.relative_to(static_dir_path))
        )

    # create destination folders and copy files over
    for src, dst in src_dst_list:
        if src.is_dir():
            dst.mkdir(exist_ok=True, parents=True)
            print(f"Creating folder: {dst}")
        else:
            shutil.copy2(src, dst)
            print(f"Copying {src} to {dst}")

    pass


def main():
    copy_static_dir_to_public()


main()
