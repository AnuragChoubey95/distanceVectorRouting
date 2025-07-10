from distanceVector import Router
"""
Create and start router_1
"""
router1 = Router("router1", 5003, {"router2" : (5004, 7), "router4" : (5006, 5)})
router1.communicate()
