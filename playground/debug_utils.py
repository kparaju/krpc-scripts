
def get_all_resources(vessel):
    """
    Get the list of resources in vessel.
    https://krpc.github.io/krpc/python/api/space-center/resources.html#SpaceCenter.Resource
    """
    return [{
        'name': r.name,
        'amount': r.amount
    } for r in vessel.resources.all]
