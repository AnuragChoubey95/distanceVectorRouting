"""
distanceVector.py
Submitted towards the completion of Project-5
of the course CSCI-651: Foundations of Computer Networks. The following
program defines a class named Router that implements the functionality of
a real world router. It can send, receive and process distance vectors from
its neighbors. 

Instructor: Minseok Kwon

Grader: Dharmendra Nasit

Author: Anurag Choubey (ac2255@g.rit.edu)
"""

import time
import socket
import pickle
import threading


class Router:
    """
    This class defines what our router object is and how it behaves.
    It implements only the basic functionality of creating a routing table,
    sending it, receiving it from neighbors and making updates if necessary.
    It uses UDP sockets for communicating with its neighboring Router objects.
    Sending and receiving are not sequential but are exceuted by two independent
    threads.  

    Methods:
        create_table
        print_table
        update_table
        send_dvr
        receive_dvr
        communicate
    """

    __slots__ = "id", "port", "neighbors", "table" 

    #global list of all routers on the network
    HOSTS = {"router1", "router2", "router3", "router4"}
    #network address of router
    IP_ADDRESS = 'localhost'
    #Input stream buffer size
    BUFFER = 2048
    #Our value for infinity, based on RFC 2453
    INFINITY = 16


    def __init__(self, id:str, port:int, neighbors:dict) -> None:
        """
        Constructs the object from the parameters
        """
        self.id = id
        self.port = port
        self.neighbors = neighbors
        self.table = self.create_table()


    def create_table(self) -> list:
        """
        Looks for the routers that are its immediate neighbors,
        and connects them to itself.
        Note: Link costs are hardcoded, but can be freely edited 
        by whoever has the source code.
        """
        routing_table = {}

        for each in Router.HOSTS:
            if each == self.id:
                pass
            if each in self.neighbors.keys():
                entry = (self.neighbors[each][1], each)
                routing_table[each] = entry
            else:
                pass
        return routing_table
    

    def print_table(self, table : list):
        """
        How to interpret the Output:
            each row tells you :
            router id : (cost to get there, next hop)
        """
        for each in table:
            print(f"{each}:{table[each]}")
        print("-------------------------------")


    def update_table(self, router):
        """
        Unpacks the incoming router table from its neighbor,
        adds a new entry if previously not known by self.
        And if a more optimal path is found to an
        existing entry, the cost and next hop are likewise updated.
        """
        for each in router.table:
            if each not in self.neighbors.keys() and each != self.id:
                #add new unseen entry
                if each not in self.table: 
                    self.table[each] = (self.neighbors[router.id][1] + router.neighbors[each][1], router.id)
                else:
                    # entry in table but cheaper found
                    if self.table[each][0] > self.table[router.id][0] + router.table[each][0]: 
                        self.table[each] = (Router.INFINITY ,router.id) if self.table[router.id][0] + router.table[each][0] > Router.INFINITY else (self.table[router.id][0] + router.table[each][0], router.id)
            if each in self.neighbors.keys():
                #if direct neigbors change their cost, eg. - Router is down, make changes in that case as well.
                if self.table[each][0] > self.neighbors[each][1]:
                    self.table[each] = (self.neighbors[each][1], each)

                
    def send_dvr(self):
        """
        Send the router object over a Datagram socket.
        """
        while True:
            for each in self.neighbors:
                my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                address = (Router.IP_ADDRESS, self.neighbors[each][0])
                my_socket.sendto(pickle.dumps(self), address)
                my_socket.close()
                time.sleep(1)


    def receive_dvr(self):
        """
        Receives the incoming router object, unpacks it
        and sends it to the update and print methods.
        If a neighbor is unresponsive for 4 calls or more,
        it treats it as down and changes the link cost to 
        infinity.
        """
        i = 0
        count_0, count_1 = 0,0
        access_key = threading.Lock()
        while True:
            i += 1
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            my_socket.settimeout(2.25)
            address = (Router.IP_ADDRESS, self.port)
            try:
                my_socket.bind(address)
                data, address = my_socket.recvfrom(Router.BUFFER)
                decoded = pickle.loads(data)
                
                if decoded.id == list(self.neighbors.keys())[0]:
                    count_0 = 0
                    count_1 += 1
                elif decoded.id == list(self.neighbors.keys())[1]:
                    count_1 = 0
                    count_0 += 1

                with access_key:
                    print(f"Updating with table received from {decoded.id}")
                    self.update_table(decoded)
                    if count_0 > 4:
                        print(f"{list(self.neighbors.keys())[0]} is down")
                        self.table[list(self.neighbors.keys())[0]] = (Router.INFINITY, list(self.neighbors.keys())[0])
                        for each in decoded.table:
                            if each not in self.neighbors.keys() and each != self.id:
                                self.table[each] = (Router.INFINITY, decoded.id) if self.table[decoded.id][0] + decoded.table[each][0] > Router.INFINITY else (self.table[decoded.id][0] + decoded.table[each][0], decoded.id) 
                    elif count_1 > 4:
                        print(f"{list(self.neighbors.keys())[1]} is down")
                        self.table[list(self.neighbors.keys())[1]] = (Router.INFINITY, list(self.neighbors.keys())[1])
                        for each in decoded.table:
                            if each not in self.neighbors.keys() and each != self.id:
                                self.table[each] = (Router.INFINITY, decoded.id) if self.table[decoded.id][0] + decoded.table[each][0] > Router.INFINITY else (self.table[decoded.id][0] + decoded.table[each][0], decoded.id)
                    self.print_table(self.table)
            except Exception as e:
                print(e)
                print("-------------------------------")
                my_socket.close()
            if i % 2 == 0:
                print("-------------------------------------------------------------")
                i = 0
                

    def communicate(self):
        """
        Sets up the communication by starting
        the sender and receiver thread.
        """
        print("\nROUTER ON!\n")
        print(f"ROUTING TABLE OF {self.id}\n{self.table}\n----------------------------------------------------------------------------")
        sender_thread = threading.Thread(target=self.send_dvr)
        receiver_thread = threading.Thread(target=self.receive_dvr)
        sender_thread.start()
        receiver_thread.start()