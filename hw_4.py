import aiopath
import aioshutil
import asyncio
import logging
from argparse import ArgumentParser

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def read_folder(
    source_folder: aiopath.AsyncPath, output_folder: aiopath.AsyncPath
):
    try:
        logger.info(f"Starting to process folder {source_folder}")
        if not await source_folder.is_dir():
            logger.error(f"Source folder {source_folder} does not exist!")
            return

        # Ensure the output folder exists
        if not await output_folder.exists():
            await output_folder.mkdir(parents=True, exist_ok=True)

        # Read files from source folder and create tasks for copying them
        tasks = [copy_file(file, output_folder) for file in await async_walk(source_folder)]
        await asyncio.gather(*tasks)

        logger.info(f"Finished processing folder {source_folder}")
    except Exception as e:
        logger.error(f"Error processing folder {source_folder}: {e}")


async def copy_file(file: aiopath.AsyncPath, output_folder: aiopath.AsyncPath):
    try:
        logger.info(f"Started copying file {file.name}")
        extension = file.suffix[1:].lower()
        subfolder = output_folder / extension

        if not await subfolder.exists():
            await subfolder.mkdir(parents=True, exist_ok=True)

        target_file = subfolder / file.name
        if file != target_file:
            await aioshutil.copy(file, target_file)
            logger.info(f"File {file.name} copied to {subfolder}")
        else:
            logger.info(f"File {file.name} is already in the target location")
    except Exception as e:
        logger.error(f"Error copying file {file}: {e}")


async def async_walk(folder: aiopath.AsyncPath):
    # Recursively walk through all files in the folder, including subfolders
    return [path async for path in folder.rglob("*") if await path.is_file()]


async def main():
    parser = ArgumentParser(description="Sort files by extension")
    parser.add_argument("source", type=str, help="Source folder path")
    parser.add_argument("output", type=str, help="Target folder path")
    args = parser.parse_args()

    source_folder = aiopath.AsyncPath(args.source)
    output_folder = aiopath.AsyncPath(args.output)

    await read_folder(source_folder, output_folder)


if __name__ == "__main__":
    asyncio.run(main())
