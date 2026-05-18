import asyncio
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')

async def test(number:int) -> dict:
    if number % 2 != 0:
        raise ValueError(f'{number} is not even')
    else:
        return {'num':number, 'half':number // 2}
    
async def try_except(number:int) -> str:
    try:
        if type(number) != int:
            raise TypeError(f'{number} is {type(number)}, not int')
        else:
            if number % 2 != 0:
                raise ValueError(f'{number} is not even')
            else:
                return f'Half of {number} is {number // 2}.'
    except ValueError as ve:
        logger.warning(ve)
        raise
    except TypeError as te:
        logger.error(te)
        raise

async def test2(number:int) -> int:
    max_attempts = 3
    for a in range(max_attempts):
        try:
            if number % 2 != 0:
                raise ValueError(f'{number} is not even')
            else:
                result = number // 2
                break
        except ValueError:
            logging.warning(f'ValueError for {number}. Retrying attempt {a+1}...')
    else:
        raise RuntimeError(f'Maximum number of retries hit for {number}')
    return result
    
async def main():
    # tasks = [try_except(i) for i in range(10)]
    # tasks.append(try_except('string'))
    # # results = await asyncio.gather(*tasks, return_exceptions = False)
    # results_re = await asyncio.gather(*tasks, return_exceptions = True)
    # # print('Return Exceptions = False:\n')
    # # for r in results:
    # #     print(f'{type(r)}\t{r}')
    # print('\nReturn Exceptions = True:\n')
    # for r in results_re:
    #     print(f'{type(r)}\t{r}')
    tasks = [test2(i) for i in range(3)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    print(results)

if __name__ == '__main__':
    asyncio.run(main())