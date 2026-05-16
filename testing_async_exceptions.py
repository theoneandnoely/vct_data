import asyncio
import logging

logger = logging.getLogger(__name__)

async def test(number:int) -> str:
    if number % 2 != 0:
        raise ValueError(f'{number} is not even')
    else:
        return f'Half of {number} is {number // 2}.'
    
async def try_except(number:int) -> str:
    try:
        if number % 2 != 0:
            raise ValueError(f'{number} is not even')
        else:
            return f'Half of {number} is {number // 2}.'
    except ValueError:
        logger.error(f'{number} is not even')
    
async def main():
    tasks = [test(i) for i in range(10)]
    # results = await asyncio.gather(*tasks, return_exceptions = False)
    results_re = await asyncio.gather(*tasks, return_exceptions = True)
    # print('Return Exceptions = False:\n')
    # for r in results:
    #     print(f'{type(r)}\t{r}')
    print('\nReturn Exceptions = True:\n')
    for r in results_re:
        print(f'{type(r)}\t{r}')

if __name__ == '__main__':
    asyncio.run(main())