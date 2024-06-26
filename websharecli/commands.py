import sys

from websharecli import api
from websharecli.config import CONFIG
from websharecli.data import File, filter_unique, filter_extensions, filter_exclude
from websharecli.terminal import T


def _get_link(files, query=None, ignore_vip=False):
    """Get first available link from list of file candidates."""
    for file_ in files:
        try:
            link = api.file_link_by_id(file_.ident, ignore_vip=ignore_vip)
        except api.LinkUnavailableException:
            if query is not None:
                print(f'{query} {T.yellow}SKIP{T.normal}: {file_.name}', file=sys.stderr)
            continue
        else:
            return link, file_
    return None, None


def link_search(query, verbose=False, exclude=None, ignore_vip=False):
    """Get download link(s) for files that match the search query"""
    results = []
    filenames = []
    not_found = 0
    try:
        for q in query_complete_wildcard(query):
            files = link_list(q, limit=3, exclude=exclude)
            link, file_ = _get_link(files, query=q, ignore_vip=ignore_vip)
            if link is not None:
                not_found = 0
                results.append(link)
                filenames.append(file_.name)
                print(f'{q} {T.green}OK{T.normal}: {file_.name}', file=sys.stderr)
            else:
                not_found += 1
                print(f'{q} {T.red}NOT FOUND{T.normal}', file=sys.stderr)
                if not_found >= 3:
                    if verbose:
                        print('Aborting after 3 failures', file=sys.stderr)
                    break
    except KeyboardInterrupt:
        pass
    return results, filenames


def link_list(query, limit=None, types=CONFIG.types, exclude=None):
    """Search and filter results based on quality."""
    if exclude is None:
        exclude = []
    exclude.extend(CONFIG.exclude)
    results = filter_exclude(filter_extensions(filter_unique(get_files(query)), types), exclude)
    if limit:
        results = results[:limit]
    return results


def get_files(query):
    """Perform query for every configured quality and return all results"""
    results = []
    for q in query_expand(query, CONFIG.quality):
        for entry in api.search(q):
            file_ = File(**entry)
            if file_.matches_query(q):
                results.append(file_)
    return results


def normalize_query(query):
    """Lowercase words and use only unique ones"""
    normalized = []
    for word in query.split(' '):
        word = word.lower()
        if word and word not in normalized:
            normalized.append(word)
    return ' '.join(normalized)


def query_expand(query, options=None):
    """Create multiple queries by extending it by some options"""
    query = normalize_query(query)
    if not options:
        return [query]
    results = []
    for option in options:
        results.append(normalize_query(query + ' ' + option))
    return results


def query_complete_wildcard(query):
    """Find asterisk ('*') and replace with numbers from 00 to 99"""
    if '*' not in query:
        return [query]
    return [query.replace('*', f'{i:02d}') for i in range(100)]
