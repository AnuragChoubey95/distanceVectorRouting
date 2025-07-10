from distanceVector import Router
"""
Create and start router_3
"""
router3 = Router("router3", 5005, {"router2" : (5004, 4), "router4" : (5006, 1)})
router3.communicate()