import asyncio

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from apps.wallet.schemas import SendTransaction, WalletImport
from config.settings import settings

data = {}

@pytest.mark.anyio
async def test_create_wallet(client: AsyncClient, fastapi_app: FastAPI):
    url = fastapi_app.url_path_for("create-wallet")
    response = await client.get(
        url,
    )
    te = response.json()
    data["address"] = te.get("address")
    data["public_key"] = te.get("public_key")
    data["private_key"] = te.get("private_key")
    data["mnemonic"] = te.get("mnemonic")
    print(response.json())
    assert response.status_code == 201


@pytest.mark.anyio
async def test_get_wallets_list(client: AsyncClient, fastapi_app: FastAPI):
    url = fastapi_app.url_path_for("get_wallets")
    payload = {"private_key": data.get("private_key")}
    response = await client.post(
        url,
        json=payload
    )
    data["address_list"] = response.json()
    assert response.status_code == 200


@pytest.mark.anyio
async def test_create_derivations(client: AsyncClient, fastapi_app: FastAPI):
    url = fastapi_app.url_path_for("create_derivations")
    payload = {"mnemonic": data.get("mnemonic")}
    response = await client.post(
        url,
        json=payload
    )
    assert response.status_code == 201



@pytest.mark.anyio
async def test_create_derivations_invalid(client: AsyncClient, fastapi_app: FastAPI):
    url = fastapi_app.url_path_for("create_derivations")
    payload = {"mnemonic": data.get("mnemonic") + "1"}
    response = await client.post(
        url,
        json=payload
    )
    assert response.status_code == 400



@pytest.mark.anyio
async def test_import_wallet(client: AsyncClient, fastapi_app: FastAPI):
    url = fastapi_app.url_path_for("import_wallet")
    payload = WalletImport(
        private_key=settings.TEST_TRX_PRIVATE,
    )
    response = await client.post(
        url,
        json=payload.dict()
    )
    print(response.json())
    assert response.status_code == 201


@pytest.mark.anyio
async def test_send_transaction(client: AsyncClient, fastapi_app: FastAPI):
    url = fastapi_app.url_path_for("send_transaction")
    payload = SendTransaction(
        from_address=settings.TEST_TRX_PUBLIC,
        to_address=settings.TEST_PURPOSE_TRX_ADDRESS,
        private_key=settings.TEST_TRX_PRIVATE,
        value=0.0000
    )
    response = await client.post(
        url,
        json=payload.dict()
    )
    assert response.status_code == 201


@pytest.mark.anyio
async def test_get_balance(client: AsyncClient):
    url = f'/api/ethereum-wallet/get-balance/{data.get("address")}/'
    response = await client.get(
        url,
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_get_transactions(client: AsyncClient):
    url = f'/api/ethereum-wallet/get-wallet-transactions/{data.get("address")}/'
    response = await client.get(
        url,
    )
    assert response.status_code == 200



