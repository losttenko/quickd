#!/usr/bin/env python3
import sys

from playwright.sync_api import Playwright, sync_playwright
import win32clipboard


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()

    # Open new page
    page = context.new_page()

    data = read_clipboard()
    # Go to https://dscan.info/
    page.goto("https://dscan.info/")

    paste_dscan(page, data)

    with page.expect_navigation():
        page.locator("input[type=\"submit\"]").click()
        page.wait_for_load_state("networkidle")
        url = page.url

        jcode = get_jcode(page)

        page.goto(f"https://eve-wh.space/{jcode}")

        effect, whclass = get_hole_data(page)
        output = create_output(effect, url, whclass, jcode)
        load_clipboard(output)
    # ---------------------
    context.close()
    browser.close()


def create_output(effect, url, whclass, jcode):
    output = "QUICKD: \n Dscan: " + url + "\n Class: " + whclass + "\n Effect: " + effect + "\n Zkill: " + f"https://zkillboard.com/system/{jcode}/"
    return output


def read_clipboard():
    win32clipboard.OpenClipboard()
    return win32clipboard.GetClipboardData()


def paste_dscan(page, data):
    page.locator("textarea[name=\"paste\"]").click()
    page.locator("textarea[name=\"paste\"]").fill(data)


def load_clipboard(output):
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(output, win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()


def get_hole_data(page):
    for line in page.content().split("\n"):
        if "WH class" in line:
            whclass = line.split(">")[1].split("<")[0].strip()
        elif "current_effect" in line:
            effect = line.split(">")[1].split("<")[0].strip()
    return effect, whclass


def get_jcode(page):
    jcode = None
    for line in page.content().split("\n"):
        if ">System" in line:
            jcode = line.split()[5].split('/')[-1].strip('"')
    if jcode is not None:
        return jcode
    sys.exit()


with sync_playwright() as playwright:
    run(playwright)
