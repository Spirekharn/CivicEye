"""
complaints/location_router.py

Bangladesh location → City Corporation auto-router.
When a citizen types a location like "Dhanmondi" or "Gulshan",
this module figures out which city corporation it belongs to
so the complaint can be routed to the right department.
"""

# Keyword → city corporation code mapping
# Built from Bangladesh administrative knowledge
BD_LOCATION_MAP = {
    # Dhaka North City Corporation (DNCC)
    'gulshan': 'DNCC', 'banani': 'DNCC', 'uttara': 'DNCC',
    'mirpur': 'DNCC', 'mohakhali': 'DNCC', 'badda': 'DNCC',
    'khilkhet': 'DNCC', 'turag': 'DNCC', 'pallabi': 'DNCC',
    'cantonment': 'DNCC', 'tejgaon': 'DNCC', 'rampura': 'DNCC',
    'khilgaon': 'DNCC', 'baridhara': 'DNCC',

    # Dhaka South City Corporation (DSCC)
    'dhanmondi': 'DSCC', 'old dhaka': 'DSCC', 'motijheel': 'DSCC',
    'lalbagh': 'DSCC', 'hazaribagh': 'DSCC', 'kotwali': 'DSCC',
    'sutrapur': 'DSCC', 'wari': 'DSCC', 'shyampur': 'DSCC',
    'kadamtali': 'DSCC', 'jatrabari': 'DSCC', 'azimpur': 'DSCC',
    'new market': 'DSCC', 'elephant road': 'DSCC', 'kalabagan': 'DSCC',
    'mohammadpur': 'DSCC', 'shahbag': 'DSCC', 'ramna': 'DSCC',
    'paltan': 'DSCC', 'gopibagh': 'DSCC',

    # Narayanganj City Corporation (NCC)
    'narayanganj': 'NCC', 'fatullah': 'NCC', 'siddhirganj': 'NCC',

    # Gazipur City Corporation (GCC)
    'gazipur': 'GCC', 'tongi': 'GCC', 'kaliakair': 'GCC',

    # Chattogram City Corporation (CCC)
    'chattogram': 'CCC', 'chittagong': 'CCC', 'agrabad': 'CCC',
    'pahartali': 'CCC', 'halishahar': 'CCC', 'nasirabad': 'CCC',
    'panchlaish': 'CCC', 'kotwali ctg': 'CCC', 'double mooring': 'CCC',

    # Sylhet City Corporation (SCC)
    'sylhet': 'SCC', 'zindabazar': 'SCC', 'ambarkhana': 'SCC',

    # Rajshahi City Corporation (RCC)
    'rajshahi': 'RCC', 'boalia': 'RCC', 'motihar': 'RCC',

    # Khulna City Corporation (KCC)
    'khulna': 'KCC', 'khalishpur': 'KCC', 'sonadanga': 'KCC',

    # Barishal City Corporation (BCC)
    'barishal': 'BCC', 'barisal': 'BCC', 'kotwali bsl': 'BCC',

    # Mymensingh City Corporation (MCC)
    'mymensingh': 'MCC',

    # Cumilla City Corporation (COCC)
    'cumilla': 'COCC', 'comilla': 'COCC', 'kandirpar': 'COCC',
    'tomsom bridge': 'COCC', 'shasan': 'COCC', 'cumilla sadar': 'COCC',

    # Rangpur City Corporation (RNCC)
    'rangpur': 'RNCC', 'mahiganj': 'RNCC', 'modern more': 'RNCC',
    'rangpur sadar': 'RNCC', 'shapla chattar': 'RNCC',
}


def detect_city_corp(location_text):
    """
    Takes a free-text location string and returns the best-matching
    city corporation code. Defaults to DSCC (Dhaka South) if unknown,
    since that covers central Dhaka where most complaints originate.
    """
    if not location_text:
        return 'DSCC'
    lower = location_text.lower()
    for keyword, corp in BD_LOCATION_MAP.items():
        if keyword in lower:
            return corp
    # Generic Dhaka check before falling back
    if 'dhaka' in lower:
        return 'DSCC'
    return 'DSCC'


def get_department_for_complaint(category, city_corp):
    """
    Given a complaint category and city corporation, find the matching
    active department. Returns None if no match (admin will assign manually).
    """
    from departments.models import Department
    # Normalize: 'other' → use 'admin_dept'
    slug = category if category != 'other' else 'admin_dept'
    return Department.objects.filter(
        slug=slug,
        city_corp=city_corp,
        is_active=True
    ).first()
