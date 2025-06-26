import requests

def check_proxy(proxy: str, test_url: str = "https://httpbin.org/ip", timeout: int = 10) -> None:
    proxy_dict = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}",
    }

    try:
        response = requests.get(test_url, proxies=proxy_dict, timeout=timeout)
        response.raise_for_status()
        ip_info = response.json()
        print(f"[✅] Proxy {proxy} is working. IP seen: {ip_info['origin']}")
    except requests.RequestException as e:
        print(f"[❌] Proxy {proxy} failed: {e}")

def main():
    proxies = [
        "37.48.118.4:13151",
        "5.79.66.2:13151",
    ]

    for proxy in proxies:
        check_proxy(proxy)

if __name__ == "__main__":
    main()
