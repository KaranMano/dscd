# Documentation

This project is a simple marketplace system implemented using gRPC in Python. It allows sellers to register, sell items, update item details, delete items, and display items. Buyers can search for items, buy items, add items to their wishlist, and rate items.

## Commands

The seller provides the following commands:
```
        REGISTER 
        SELL <name> <category> <quantity> <description> <price-per-unit>
         Available categories: ELECTRONICS, FASHION, OTHERS
        UPDATE <itemID> <quantity> <price-per-unit>
        DELETE <itemID>
        DISPLAY
        EXIT
```
The buyer provides the following commands:
```
        SEARCH <category> <name>
         Available categories: ELECTRONICS,FASHION, OTHERS, ANY
        BUY <itemID> <quantity>
        WISH <itemID>
        RATE <itemID> <rating>
        EXIT
```


## Usage

1. Start the server: `python3 market.py`
2. Start the seller portal: `python3 seller.py [-m MARKET]`
3. Start the buyer portal: `python3 buyer.py [-m MARKET]`

### Command Usage

#### seller.py

```
usage: seller.py [-h] [-m MARKET]

optional arguments:
  -h, --help            show this help message and exit
  -m MARKET, --market MARKET
                        The IP address of the market
```

#### buyer.py

```
usage: buyer.py [-h] [-m MARKET]

optional arguments:
  -h, --help            show this help message and exit
  -m MARKET, --market MARKET
                        The IP address of the market
```

## Dependencies

- Python 3
- gRPC for Python