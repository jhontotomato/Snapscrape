import category_translator
import snap_scrape
import asyncio
import cleaner

async def main():
    
    await snap_scrape.main()
    await category_translator.main()
    await cleaner.main()
    
    
if __name__ == "__main__":
    asyncio.run(main())