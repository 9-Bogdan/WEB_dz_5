import sys
import asyncio
import aiohttp
import platform
from datetime import datetime, timedelta
import logging


async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    r = await resp.json()
                    return r
                logging.error(f"Error status: {resp.status} for {url}")
                return None
        except aiohttp.ClientConnectorError as err:
            logging.error(f"Connection error: {str(err)}")
            return None


async def main(number_of_days, new_currency=None):
    date = datetime.now().date()
    if number_of_days == 0:
        result = await request(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={datetime.strftime(date,"%d.%m.%Y")}')
        if result:
            rates = result.get("exchangeRate")
            usd, = list(
                filter(lambda element: element["currency"] == "USD", rates))
            usd_dict = {
                f"USD": {"sale": usd['saleRateNB'], "purchase": usd['purchaseRate']}}
            eur, = list(
                filter(lambda element: element["currency"] == "EUR", rates))
            cor_date = datetime.strftime(date, "%d.%m.%Y")
            eur_dict = {
                f"EUR": {"sale": eur['saleRateNB'], "purchase": eur['purchaseRate']}}
            eur_dict.update(usd_dict)
            last_dict = dict()
            if new_currency != None:
                try:
                    exc, = filter(
                        lambda element: element["currency"] == new_currency, rates)
                    exc_dict = {
                        f"{new_currency}": {"sale": exc['saleRateNB'], "purchase": exc['purchaseRate']}}
                    eur_dict.update(exc_dict)
                    last_dict[f"{cor_date}"] = eur_dict
                except ValueError:
                    return "Invalid currency!"
            else:
                last_dict[f"{cor_date}"] = eur_dict
            return [last_dict]
        else:
            return "Failed to retrieve data"
    elif 0 < number_of_days <= 10:
        last_dict = dict()
        for i in range(1, number_of_days + 1):
            result = await request(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={datetime.strftime(date - timedelta(days=i),"%d.%m.%Y")}')
            if result:
                rates = result.get("exchangeRate")
                usd, = list(
                    filter(lambda element: element["currency"] == "USD", rates))
                usd_dict = {
                    f"USD": {"sale": usd['saleRateNB'], "purchase": usd['purchaseRate']}}
                eur, = list(
                    filter(lambda element: element["currency"] == "EUR", rates))
                cor_date = datetime.strftime(
                    date - timedelta(days=i), "%d.%m.%Y")
                eur_dict = {
                    f"EUR": {"sale": eur['saleRateNB'], "purchase": eur['purchaseRate']}}
                eur_dict.update(usd_dict)
                if new_currency != None:
                    try:
                        exc, = filter(
                            lambda element: element["currency"] == new_currency, rates)
                        exc_dict = {
                            f"{new_currency}": {"sale": exc['saleRateNB'], "purchase": exc['purchaseRate']}}
                        eur_dict.update(exc_dict)
                        last_dict[f"{cor_date}"] = eur_dict
                    except ValueError:
                        return "Invalid currency!"
                else:
                    last_dict[f"{cor_date}"] = eur_dict
            else:
                return "Failed to retrieve data or currency"
        return [last_dict]
    else:
        return "You entered an incorrect number of days"


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    if len(sys.argv) == 2:
        number_of_days = int(sys.argv[1])
        result = asyncio.run(main(number_of_days))
    elif len(sys.argv) == 3:
        number_of_days = int(sys.argv[1])
        new_currency = sys.argv[2]
        result = asyncio.run(main(number_of_days, new_currency))
    print(result)
