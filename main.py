
from playwright.sync_api import sync_playwright, Page


def get_urls_client_page(client_endpoint: str, pass_page: Page):
    pass_page.goto(client_endpoint)
    rows = pass_page.locator('//h3[contains(text(),"Encentivizer Catalog Widget")]/ancestor::div[1]/p/a')
    count = rows.count()
    dict_page_url = {}
    for i in range(count):
        dict_page_url[rows.nth(i).text_content()] = rows.nth(i).get_attribute('href')
    return dict_page_url


def check_widget_in_page(pass_dict_pages: dict, pass_page: Page):
    failed_page_item = {}
    number_of_matched_items_list = []
    number_of_matched_item = 0
    for page_name, page_url in pass_dict_pages.items():
        print(page_name)
        print(page_url)
        if page_name == "Cooper Lighting":
            pass_page.goto(page_url, wait_until="domcontentloaded", timeout=90000)
            elementHandle = pass_page.wait_for_selector('iframe[title="TrustArc Cookie Consent Manager"]')
            frame = elementHandle.content_frame()
            frame.wait_for_selector('//a[text()[contains(.,"Agree and proceed")]]').click()
            pass_page.wait_for_selector('select[class="ee-widget-form-control"]')
        elif page_name == "Dialight":
            pass_page.goto(page_url, wait_until="networkidle", timeout=90000)
            # page.wait_for_selector('iframe[owner="archetype"]')
            # frame = elementHandle.content_frame()
            pass_page.locator('#onetrust-accept-btn-handler').click()
            pass_page.wait_for_selector('select[class="ee-widget-form-control"]')
        else:
            pass_page.goto(page_url, wait_until="networkidle", timeout=90000)
        if page_name == "Topaz Lighting Corp.":
            elementHandle = pass_page.wait_for_selector('iframe[src]')
            frame = elementHandle.content_frame()
            frame.wait_for_selector('select[class="ee-widget-form-control"]')
            number_of_matched_item=frame.locator('select[class="ee-widget-form-control"]').count()
        else:
            number_of_matched_item = pass_page.locator('select[class="ee-widget-form-control"]').count()
        if number_of_matched_item == 0:
            failed_page_item[page_name] = page_url
            number_of_matched_items_list.append(page_name)
    return failed_page_item, number_of_matched_items_list


def get_result_to_send(failed_page_item:dict, number_items_detail:list):
    result = ""
    number = len(number_items_detail)
    if len(failed_page_item) == 0:
        result = "Success, all the pages have expected widgets"
    else:
        result = f'Failed, there are {number} pages failed which are : {number_items_detail}'
    return result


def send_result_to_Slack(channel_id:str, token:str, result:str):
    import requests
    data = {'channel': channel_id,
            'text': result}
    headers = {'Authorization': 'Bearer ' + token}
    requests.post("https://slack.com/api/chat.postMessage", headers=headers, data=data)


if __name__ == '__main__':
    CLIENT_URL = "https://www.encentivenergy.com/livewidgets"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        dictionary_pages = get_urls_client_page(CLIENT_URL, pass_page=page)
        # dictionary_pages = {"Topaz Lighting Corp.":"https://www.topaz-usa.com/rebate-finder"}
        dict_failed_pages, list_page_name = check_widget_in_page(pass_dict_pages=dictionary_pages, pass_page=page)
        result_to_send = get_result_to_send(dict_failed_pages,list_page_name)
        send_result_to_Slack("C03EJ6VUTKL","xoxb-3517990543552-3498517567635-92h6lf0egFl8hqiYhr6jFZB2",result_to_send)
        print(dict_failed_pages)
        browser.close()
