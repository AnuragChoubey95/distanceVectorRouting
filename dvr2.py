from distanceVector import Router
"""
Create and start router_2
"""
router2 = Router("router2", 5004, {"router1" : (5003, 7), "router3" : (5005, 4)})
router2.communicate()