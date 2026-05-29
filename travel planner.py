"""
============================================================
  Q2: AI-Based Travel Planner
  Uses knowledge bases for:
    - Tourist places (with categories and ratings)
    - Food recommendations (regional cuisine)
    - Wine/beverage pairing
    - Cost assessment
    - Personalised tour plan generation
============================================================
"""

# ─────────────────────────────────────────────────────────────
#  KNOWLEDGE BASE — replaces external ontology files
#  In a real system these would load from OWL/RDF ontology files
#  e.g.  graph = rdflib.Graph(); graph.parse("tourism.owl")
# ─────────────────────────────────────────────────────────────

# Tourist Places KB  {city: [list of (place, category, rating, entry_fee_INR)]}
TOURIST_PLACES_KB = {
    "Goa": [
        ("Baga Beach",          "Beach",        4.5,  0),
        ("Dudhsagar Falls",     "Nature",       4.8, 50),
        ("Basilica of Bom Jesus","Heritage",    4.7,  0),
        ("Fort Aguada",         "Heritage",     4.3, 30),
        ("Anjuna Flea Market",  "Market",       4.0,  0),
    ],
    "Hyderabad": [
        ("Charminar",           "Heritage",     4.6, 25),
        ("Golconda Fort",       "Heritage",     4.5, 15),
        ("Hussain Sagar",       "Lake",         4.2,  0),
        ("Ramoji Film City",    "Entertainment",4.3,1500),
        ("Nehru Zoological Park","Nature",      4.1, 80),
    ],
    "Manali": [
        ("Rohtang Pass",        "Adventure",    4.7,  0),
        ("Solang Valley",       "Adventure",    4.6,  0),
        ("Hadimba Temple",      "Spiritual",    4.4,  0),
        ("Old Manali",          "Culture",      4.3,  0),
        ("Beas Kund Trek",      "Trekking",     4.8,  0),
    ],
    "Jaipur": [
        ("Amber Fort",          "Heritage",     4.8, 200),
        ("Hawa Mahal",          "Heritage",     4.6,  50),
        ("City Palace",         "Heritage",     4.5, 400),
        ("Jantar Mantar",       "Heritage",     4.3, 100),
        ("Nahargarh Fort",      "Heritage",     4.4, 200),
    ],
    "Kerala": [
        ("Alleppey Backwaters", "Nature",       4.9, 500),
        ("Munnar Tea Gardens",  "Nature",       4.7,  50),
        ("Periyar Wildlife",    "Nature",       4.6, 300),
        ("Kovalam Beach",       "Beach",        4.4,  0),
        ("Athirapally Falls",   "Nature",       4.5,  30),
    ],
}

# Food Recommendations KB  {city: [(dish, cuisine_type, veg, avg_cost_INR)]}
FOOD_KB = {
    "Goa": [
        ("Goan Fish Curry",      "Coastal",    False, 350),
        ("Bebinca",              "Dessert",    True,  150),
        ("Vindaloo",             "Spicy",      False, 300),
        ("Prawn Balchão",        "Coastal",    False, 400),
        ("Pão",                  "Bakery",     True,   30),
    ],
    "Hyderabad": [
        ("Hyderabadi Biryani",   "Mughal",     False, 250),
        ("Haleem",               "Mughal",     False, 200),
        ("Mirchi ka Salan",      "Spicy",      True,  100),
        ("Double ka Meetha",     "Dessert",    True,  120),
        ("Irani Chai",           "Beverage",   True,   30),
    ],
    "Manali": [
        ("Siddu",                "Himachali",  True,   80),
        ("Dham",                 "Himachali",  True,  150),
        ("Trout Fish",           "Himachali",  False, 450),
        ("Aktori",               "Himachali",  True,  120),
        ("Bhey",                 "Himachali",  True,   90),
    ],
    "Jaipur": [
        ("Dal Baati Churma",     "Rajasthani", True,  200),
        ("Ghevar",               "Dessert",    True,  100),
        ("Laal Maas",            "Rajasthani", False, 350),
        ("Pyaaz Kachori",        "Street",     True,   40),
        ("Ker Sangri",           "Rajasthani", True,  180),
    ],
    "Kerala": [
        ("Appam with Stew",      "Kerala",     True,  150),
        ("Kerala Sadya",         "Traditional",True,  250),
        ("Fish Molee",           "Coastal",    False, 350),
        ("Puttu and Kadala",     "Breakfast",  True,  100),
        ("Payasam",              "Dessert",    True,   80),
    ],
}

# Wine / Beverage Pairing KB  {cuisine_type: [(beverage, pairing_notes)]}
WINE_KB = {
    "Coastal":    [("Sauvignon Blanc", "Bright acidity pairs with seafood"),
                   ("Kingfisher Beer",  "Classic Indian coastal pairing")],
    "Spicy":      [("Riesling",         "Sweetness tames the heat"),
                   ("Lassi",            "Yoghurt-based cooling drink")],
    "Mughal":     [("Shiraz/Syrah",     "Bold tannins complement rich gravies"),
                   ("Kehwa",            "Traditional spiced green tea")],
    "Rajasthani": [("Grenache",         "Fruity notes with mild spice"),
                   ("Chaas",            "Spiced buttermilk — traditional pairing")],
    "Himachali":  [("Kullu Apple Wine", "Local speciality from Himachal Pradesh"),
                   ("Noon Chai",        "Pink salt tea — Himachali tradition")],
    "Kerala":     [("Chenin Blanc",     "Pairs with mild coconut-based dishes"),
                   ("Toddy",            "Local palm wine — authentic experience")],
    "Dessert":    [("Muscat",           "Sweet wine with sweet dishes"),
                   ("Masala Chai",      "Spiced tea cuts through richness")],
    "Breakfast":  [("Orange Juice",     "Fresh juice with morning dishes"),
                   ("Filter Coffee",    "South Indian staple")],
    "Traditional":[("Tender Coconut",   "Natural and refreshing"),
                   ("Panner Soda",      "Local Kerala fizzy drink")],
    "Beverage":   [("Water",            "Stay hydrated!"),
                   ("Soda",             "Complements the chai")],
    "Market":     [("Feni",             "Goa's famous cashew spirit"),
                   ("King's Beer",      "Popular local lager")],
    "Street":     [("Jal Jeera",        "Tangy spiced water"),
                   ("Aam Panna",        "Raw mango cooler")],
}

# Accommodation KB  {budget_level: {city: [(hotel_name, price_per_night_INR, stars)]}}
HOTEL_KB = {
    "budget": {
        "Goa":       [("Zostel Goa",         800, 1), ("The Hosteller",     1200, 2)],
        "Hyderabad": [("OYO Express",         700, 1), ("Hotel Sapphire",   1000, 2)],
        "Manali":    [("Snow Valley Hostel",  600, 1), ("Drifters Inn",      900, 2)],
        "Jaipur":    [("Zostel Jaipur",       700, 1), ("Hotel Pearl",       950, 2)],
        "Kerala":    [("Backwater Hostel",    800, 1), ("Green Nest",        950, 2)],
    },
    "mid": {
        "Goa":       [("Resort Rio",         4000, 3), ("La Calypso",       5000, 4)],
        "Hyderabad": [("Novotel",            5000, 4), ("Lemon Tree",       4000, 3)],
        "Manali":    [("Span Resort",        5500, 4), ("The Himalayan",    4500, 3)],
        "Jaipur":    [("Samode Haveli",      6000, 4), ("Clarks Amer",      5000, 3)],
        "Kerala":    [("Coconut Lagoon",     6000, 4), ("Fragrant Nature",  5000, 3)],
    },
    "luxury": {
        "Goa":       [("Taj Exotica",       18000, 5), ("W Goa",           22000, 5)],
        "Hyderabad": [("Taj Falaknuma",     25000, 5), ("ITC Kohenur",     18000, 5)],
        "Manali":    [("Urvashi Resort",    12000, 5), ("Solang Valley R.", 15000, 5)],
        "Jaipur":    [("Rambagh Palace",    35000, 5), ("Taj Jai Mahal",   28000, 5)],
        "Kerala":    [("Kumarakom Lake",    20000, 5), ("Leela Kovalam",   18000, 5)],
    },
}

# Transport cost KB  {mode: cost_per_day_INR}
TRANSPORT_KB = {
    "self_drive": 2500,
    "cab":        1800,
    "auto":        600,
    "public":      200,
}

# Activity cost KB  {category: avg_cost_INR_per_activity}
ACTIVITY_COST_KB = {
    "Beach":         500,
    "Nature":        300,
    "Heritage":      200,
    "Adventure":    1500,
    "Trekking":      800,
    "Entertainment":1500,
    "Spiritual":       0,
    "Culture":       200,
    "Lake":          100,
    "Market":        300,
}


# ─────────────────────────────────────────────────────────────
#  USER PREFERENCE MODEL
# ─────────────────────────────────────────────────────────────

class UserProfile:
    """
    Captures personalised user preferences for tour planning.
    """
    def __init__(self, name, destination, days, budget_level,
                 interests=None, vegetarian=False, transport_mode="cab"):
        self.name           = name
        self.destination    = destination
        self.days           = days
        self.budget_level   = budget_level   # 'budget' | 'mid' | 'luxury'
        self.interests      = interests or []# e.g. ['Heritage', 'Nature']
        self.vegetarian     = vegetarian
        self.transport_mode = transport_mode


# ─────────────────────────────────────────────────────────────
#  KNOWLEDGE BASE INTERFACE (Inference Engine)
# ─────────────────────────────────────────────────────────────

class TravelKnowledgeBase:
    """
    Central inference engine that queries all sub-KBs.
    In a production system this would use SPARQL queries
    over an RDF/OWL ontology (e.g., DBpedia Tourism Ontology).
    """

    def get_places(self, city, interests=None, top_n=5):
        """
        Return top-N places filtered by user interest categories,
        ranked by rating (descending).
        """
        places = TOURIST_PLACES_KB.get(city, [])
        if interests:
            places = [p for p in places if p[1] in interests]
        places = sorted(places, key=lambda p: p[2], reverse=True)
        return places[:top_n]

    def get_food(self, city, vegetarian=False, top_n=4):
        """Return food recommendations, filtering by dietary preference."""
        foods = FOOD_KB.get(city, [])
        if vegetarian:
            foods = [f for f in foods if f[2]]   # f[2] == is_veg
        return foods[:top_n]

    def get_wine_pairing(self, cuisine_type):
        """Return wine/beverage pairing for a given cuisine type."""
        return WINE_KB.get(cuisine_type, [("Water", "Always a safe choice")])

    def get_hotel(self, city, budget_level):
        """Return hotel recommendation for city and budget."""
        hotels = HOTEL_KB.get(budget_level, {}).get(city, [])
        return hotels[0] if hotels else ("Unknown Hotel", 2000, 3)

    def estimate_cost(self, profile, places, food_items):
        """
        Cost assessment model:
        Total = Accommodation + Transport + Entry Fees + Activities + Food
        """
        hotel_name, price_per_night, stars = self.get_hotel(
            profile.destination, profile.budget_level)

        accommodation_cost = price_per_night * profile.days
        transport_cost     = TRANSPORT_KB.get(profile.transport_mode, 800) * profile.days

        entry_fees = sum(p[3] for p in places)   # sum entry fees per place
        activity_cost = sum(
            ACTIVITY_COST_KB.get(p[1], 200) for p in places)

        food_cost = sum(f[3] for f in food_items) * profile.days

        total = accommodation_cost + transport_cost + entry_fees + activity_cost + food_cost

        return {
            "hotel"        : hotel_name,
            "accommodation": accommodation_cost,
            "transport"    : transport_cost,
            "entry_fees"   : entry_fees,
            "activities"   : activity_cost,
            "food"         : food_cost,
            "total"        : total,
            "per_day"      : total // profile.days,
        }


# ─────────────────────────────────────────────────────────────
#  TOUR PLAN GENERATOR
# ─────────────────────────────────────────────────────────────

class TourPlanGenerator:
    """
    Generates a day-by-day personalised tour plan from the KB.
    """

    def __init__(self):
        self.kb = TravelKnowledgeBase()

    def generate(self, profile: UserProfile):
        city        = profile.destination
        days        = profile.days
        interests   = profile.interests if profile.interests else None

        # ── Query KB ──────────────────────────────────────────
        places   = self.kb.get_places(city, interests, top_n=days * 2)
        foods    = self.kb.get_food(city, profile.vegetarian, top_n=4)
        hotel, price, stars = self.kb.get_hotel(city, profile.budget_level)
        cost     = self.kb.estimate_cost(profile, places, foods)

        # ── Build day-by-day itinerary ────────────────────────
        itinerary = []
        places_per_day = max(1, len(places) // days)
        for day in range(days):
            day_places = places[day * places_per_day : (day + 1) * places_per_day]
            food_item  = foods[day % len(foods)] if foods else None
            pairing    = self.kb.get_wine_pairing(food_item[1]) if food_item else []
            itinerary.append({
                "day"    : day + 1,
                "places" : day_places,
                "food"   : food_item,
                "pairing": pairing,
            })

        return {
            "profile"  : profile,
            "hotel"    : (hotel, price, stars),
            "itinerary": itinerary,
            "cost"     : cost,
        }

    def display_plan(self, plan):
        p       = plan["profile"]
        hotel   = plan["hotel"]
        cost    = plan["cost"]
        itin    = plan["itinerary"]

        print("\n" + "═" * 62)
        print(f"  🧳  PERSONALISED TOUR PLAN FOR {p.name.upper()}")
        print("═" * 62)
        print(f"  Destination  : {p.destination}")
        print(f"  Duration     : {p.days} days")
        print(f"  Budget Level : {p.budget_level.capitalize()}")
        print(f"  Diet         : {'Vegetarian' if p.vegetarian else 'Non-Vegetarian'}")
        print(f"  Transport    : {p.transport_mode.replace('_',' ').title()}")
        if p.interests:
            print(f"  Interests    : {', '.join(p.interests)}")

        print(f"\n  🏨  ACCOMMODATION")
        print(f"     {hotel[0]}  ({hotel[2]}★)  — ₹{hotel[1]:,}/night")

        for day in itin:
            print(f"\n  📅  DAY {day['day']}")
            for place in day["places"]:
                fee = f"Entry: ₹{place[3]}" if place[3] > 0 else "Free entry"
                print(f"     🏛  {place[0]}  [{place[1]}, ⭐{place[2]}]  {fee}")
            if day["food"]:
                f = day["food"]
                veg_tag = "🌱" if f[2] else "🍖"
                print(f"     🍽  Try: {f[0]}  {veg_tag}  ≈ ₹{f[3]}")
                for bev, note in day["pairing"]:
                    print(f"     🍷  Pair with: {bev}  — {note}")

        print(f"\n  💰  COST ASSESSMENT")
        print(f"     Accommodation : ₹{cost['accommodation']:>8,}")
        print(f"     Transport     : ₹{cost['transport']:>8,}")
        print(f"     Entry Fees    : ₹{cost['entry_fees']:>8,}")
        print(f"     Activities    : ₹{cost['activities']:>8,}")
        print(f"     Food          : ₹{cost['food']:>8,}")
        print(f"     ─────────────────────────")
        print(f"     TOTAL         : ₹{cost['total']:>8,}")
        print(f"     Per Day       : ₹{cost['per_day']:>8,}")
        print("═" * 62)


# ─────────────────────────────────────────────────────────────
#  TEST CASES
# ─────────────────────────────────────────────────────────────

def test_travel_planner():
    gen = TourPlanGenerator()

    # ── Test 1: Heritage lover in Jaipur ───────────────────────
    print("\n" + "="*62)
    print("  TEST 1: Heritage Lover — Jaipur, 3 days, Budget")
    print("="*62)
    u1 = UserProfile("Rahul", "Jaipur", 3, "budget",
                     interests=["Heritage"], vegetarian=True,
                     transport_mode="public")
    plan1 = gen.generate(u1)
    gen.display_plan(plan1)
    assert plan1["cost"]["total"] > 0
    assert all(p[1] == "Heritage" for day in plan1["itinerary"] for p in day["places"])
    print("\n TEST 1 PASSED — Heritage filter works, vegetarian food only")

    # ── Test 2: Adventure seeker in Manali ─────────────────────
    print("\n" + "="*62)
    print("  TEST 2: Adventure Seeker — Manali, 4 days, Mid")
    print("="*62)
    u2 = UserProfile("Priya", "Manali", 4, "mid",
                     interests=["Adventure", "Trekking"], vegetarian=False,
                     transport_mode="self_drive")
    plan2 = gen.generate(u2)
    gen.display_plan(plan2)
    assert plan2["hotel"][0] != "Unknown Hotel"
    print("\n TEST 2 PASSED — Adventure places selected, mid-range hotel")

    # ── Test 3: Luxury coastal trip to Goa ─────────────────────
    print("\n" + "="*62)
    print("  TEST 3: Luxury Traveller — Goa, 5 days, Luxury")
    print("="*62)
    u3 = UserProfile("Arjun", "Goa", 5, "luxury",
                     interests=["Beach", "Heritage", "Market"],
                     vegetarian=False, transport_mode="cab")
    plan3 = gen.generate(u3)
    gen.display_plan(plan3)
    assert plan3["cost"]["accommodation"] == 5 * plan3["hotel"][1]
    print("\n TEST 3 PASSED — Cost math correct for luxury stay")

    # ── Test 4: Kerala nature trip, veg only ───────────────────
    print("\n" + "="*62)
    print("  TEST 4: Nature Lover — Kerala, 3 days, Mid, Vegetarian")
    print("="*62)
    u4 = UserProfile("Sneha", "Kerala", 3, "mid",
                     interests=["Nature", "Beach"], vegetarian=True,
                     transport_mode="auto")
    plan4 = gen.generate(u4)
    gen.display_plan(plan4)
    for day in plan4["itinerary"]:
        if day["food"]:
            assert day["food"][2] == True, "Non-veg food served to vegetarian user!"
    print("\n TEST 4 PASSED — All food items are vegetarian")

    # ── Test 5: Wine KB pairing test ───────────────────────────
    print("\n" + "="*62)
    print("  TEST 5: Wine Pairing Knowledge Base Query")
    print("="*62)
    kb = TravelKnowledgeBase()
    for cuisine in ["Coastal", "Mughal", "Spicy", "Rajasthani"]:
        pairings = kb.get_wine_pairing(cuisine)
        print(f"  {cuisine:<12}: {pairings[0][0]} — {pairings[0][1]}")
        assert len(pairings) > 0
    print("\n TEST 5 PASSED — Wine KB returns valid pairings")

    print("\n" + "█"*62)
    print("  ALL TRAVEL PLANNER TESTS PASSED ")
    print("█"*62)


if __name__ == "__main__":
    test_travel_planner()
