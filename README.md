# hd-wallet




## _To run this project, you need to have docker and docker compose on your local machine._


For up containers in the directory with project run 
```sh
cd appdir
make up
```

or

```sh
sudo docker compose up --build
```

## Here is an example of local.env file:

###### for testing need to create database on your local machine
``` .env
TEST_POSTGRES_PASSWORD=pass
TEST_POSTGRES_USER=user
TEST_POSTGRES_DB=db

POSTGRES_PASSWORD=pass
POSTGRES_NAME=user
POSTGRES_USER=db

INFURA_API_URL=
INFURA_API_KEY=

ETHERSCAN_KEY=
ETHERSCAN_ENDPOINT=

TEST_TRX_PUBLIC=
TEST_TRX_PRIVATE=
TEST_PURPOSE_TRX_ADDRESS=
```
