import re


def convert_to_list_json(response):
    pattern = re.compile(r'(?P<position>\d+)\. (?P<title>.+?) \((?P<year>\d{4})\)')

    # Find all matches in the response
    matches = pattern.finditer(response)
    result = [{"title": match.group('title').strip(), "year": match.group('year')} for match in matches]
    return result
