def get_pages(tracks):
    res = []
    la = []
    for el in tracks:
        if len(la) != 15:
            la.append(el)
        else:
            res.append(la)
            la = []
    else:
        res.append(la)
    return res
