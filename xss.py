#!/usr/bin/env python3
import os
import time
import sys
import argparse
from urllib.parse import urlsplit, parse_qs, urlencode, urlunsplit
from colorama import Fore
import requests

def generate_payload_urls(url, payload):
    """Generate URLs with injected payloads."""
    url_combinations = []
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    if not scheme:
        scheme = 'http'
    query_params = parse_qs(query_string, keep_blank_values=True)
    for key in query_params.keys():
        modified_params = query_params.copy()
        modified_params[key] = [payload]
        modified_query_string = urlencode(modified_params, doseq=True)
        modified_url = urlunsplit((scheme, netloc, path, modified_query_string, fragment))
        url_combinations.append(modified_url)
    return url_combinations

def check_vulnerability(url, payloads):
    """Check if a URL is vulnerable to XSS."""
    vulnerable_urls = []
    total_scanned = 0
    for payload in payloads:
        payload_urls = generate_payload_urls(url, payload)
        for payload_url in payload_urls:
            total_scanned += 1
            print(Fore.YELLOW + f"[→] Scanning: {payload_url}")
            try:
                response = requests.get(payload_url, timeout=5, verify=False)
                if payload in response.text:
                    print(Fore.GREEN + f"[✓] Vulnerable: {payload_url}")
                    vulnerable_urls.append(payload_url)
                else:
                    print(Fore.RED + f"[✗] Not Vulnerable: {payload_url}")
            except requests.RequestException as e:
                print(Fore.RED + f"[!] Error: {e}")
    return vulnerable_urls, total_scanned

def load_payloads(payload_file):
    """Load payloads from a file."""
    try:
        with open(payload_file, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(Fore.RED + f"[!] Error loading payloads: {e}")
        sys.exit(1)

def save_results(vulnerable_urls, output_file):
    """Save vulnerable URLs to a file."""
    try:
        with open(output_file, "w") as file:
            for url in vulnerable_urls:
                file.write(url + "\n")
        print(Fore.GREEN + f"[✓] Results saved to: {output_file}")
    except Exception as e:
        print(Fore.RED + f"[!] Error saving results: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="XSS Scanner using requests library.")
    parser.add_argument("-f", "--file", help="Path to input file containing URLs.")
    parser.add_argument("-u", "--url", help="Scan a single URL.")
    parser.add_argument("-p", "--payloads", required=True, help="Path to payload file.")
    parser.add_argument("-o", "--output", help="Path to save vulnerable URLs.")
    args = parser.parse_args()

    # Validate input
    if not args.file and not args.url:
        print(Fore.RED + "[!] You must provide either a file of URLs (-f) or a single URL (-u).")
        sys.exit(1)
    if args.file and not os.path.isfile(args.file):
        print(Fore.RED + f"[!] Input file not found: {args.file}")
        sys.exit(1)

    # Load URLs
    if args.file:
        with open(args.file, "r") as file:
            urls = [line.strip() for line in file if line.strip()]
    else:
        urls = [args.url]

    # Load payloads
    payloads = load_payloads(args.payloads)

    # Scan URLs
    all_vulnerable_urls = []
    total_scanned = 0
    start_time = time.time()

    for url in urls:
        print(Fore.YELLOW + f"\n[→] Scanning URL: {url}")
        vulnerable_urls, scanned = check_vulnerability(url, payloads)
        all_vulnerable_urls.extend(vulnerable_urls)
        total_scanned += scanned

    # Print summary
    print(Fore.YELLOW + "\n→ Scan Complete.")
    print(Fore.GREEN + f"• Total Vulnerable URLs: {len(all_vulnerable_urls)}")
    print(Fore.GREEN + f"• Total Scanned URLs: {total_scanned}")
    print(Fore.GREEN + f"• Time Taken: {int(time.time() - start_time)} seconds")

    # Save results if output file is specified
    if args.output:
        save_results(all_vulnerable_urls, args.output)

if __name__ == "__main__":
    main()
