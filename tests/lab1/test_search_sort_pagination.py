import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.lab1


def test_search_is_case_insensitive_and_partial(client: TestClient) -> None:
    response = client.get("/products", params={"q": "proart"})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert [item["name"] for item in body["items"]] == [
        "ProArt P16",
        "ProArt Display PA279CRV",
    ]


def test_sort_by_price_descending(client: TestClient) -> None:
    response = client.get("/products", params={"sort": "price", "order": "desc"})

    assert response.status_code == 200
    prices = [item["price"] for item in response.json()["items"]]
    assert prices == sorted(prices, reverse=True)


def test_pagination_reports_total_before_slicing(client: TestClient) -> None:
    response = client.get("/products", params={"page": 2, "page_size": 2})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 6
    assert body["page"] == 2
    assert body["page_size"] == 2
    assert [item["id"] for item in body["items"]] == [3, 4]


def test_search_sort_and_pagination_can_be_combined(client: TestClient) -> None:
    response = client.get(
        "/products",
        params={
            "q": "gaming",
            "sort": "price",
            "order": "asc",
            "page": 1,
            "page_size": 2,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert [item["name"] for item in body["items"]] == [
        "TUF Gaming A15",
        "ROG Zephyrus G14",
    ]


@pytest.mark.parametrize(
    ("params", "invalid_field"),
    [
        ({"sort": "unknown"}, "sort"),
        ({"sort": "id"}, "sort"),
        ({"sort": "category"}, "sort"),
        ({"order": "sideways"}, "order"),
        ({"page": 0}, "page"),
        ({"page_size": 21}, "page_size"),
    ],
)
def test_invalid_query_parameters_return_422(
    client: TestClient,
    params: dict[str, object],
    invalid_field: str,
) -> None:
    response = client.get("/products", params=params)

    assert response.status_code == 422
    assert invalid_field in str(response.json())
