from distanceVector import Router
"""
Create and start router_4
"""
router4 = Router("router4", 5006, {"router1" : (5003, 5), "router3" : (5005, 1)})
router4.communicate()