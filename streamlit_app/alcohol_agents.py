# alcohol_agents.py

##################################
### Packages
##################################
import mesa
from mesa import Agent, Model
from mesa.time import RandomActivation
#from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
#import random
import streamlit as st
from model_two_types_mecc import PersonAgent, ServiceAgent, MECC_Model


##################################
### Person Agent Class
##################################

## creates a subclass of person agent for the alcohol model
class AlcoholModel_PersonAgent(PersonAgent):
    def __init__(self
                 , unique_id
                 , model
                ## demographics
                 , gender
                 , age
                 , deprivation

                 ## change state probability
                 , change_prob_contemplation
                 , change_prob_preparation
                 , change_prob_action

                 , lapse_prob_precontemplation
                 , lapse_prob_contemplation
                 , lapse_prob_preparation

                ## visit probability
                 , visit_prob_Job_centre
                 , visit_prob_Benefits_office
                 , visit_prob_Housing_officer
                 , visit_prob_Community_hub                
                 
                ## alcohol
                 , inital_alcohol_status = "Pre-contemplation"                 
                 ):
        super().__init__(unique_id, model)


        self.demographics = {"gender":gender
                            ,"age": age
                            ,"deprivation": deprivation}

        ## Alcohol properties
        self.alcohol_status = {"status": inital_alcohol_status
                                ,"time": 0}

        self.change_prob_contemplation = change_prob_contemplation
        self.change_prob_preparation = change_prob_preparation
        self.change_prob_action = change_prob_action

        self.lapse_prob_precontemplation = lapse_prob_precontemplation
        self.lapse_prob_contemplation = lapse_prob_contemplation
        self.lapse_prob_preparation = lapse_prob_preparation

        ## Visit properties
        self.visit_prob = { 
                  "Job Centre'": visit_prob_Job_centre
                 ,"Benefits Office": visit_prob_Benefits_office
                 ,"Housing Officer": visit_prob_Housing_officer
                 ,"Community Hub": visit_prob_Community_hub }

    ## function to update status
    def update_status(self,start,end,probability):
        if (
            self.alcohol_status["status"] == start &
                self.random.uniform(0, 1) <= probability
            ):
            self.alcohol_status = {"status": end
                                    ,"time": 0}
            
    def update_alcohol_status(self):
        '''
        cycles through the possible status updating each one
        then reverse order for lapses
        '''
        ## Positive Change
        self.update_status(self,"Pre-contemplation","Contemplation",self.change_prob_contemplation)
        self.update_status(self,"Contemplation","Preparation",self.change_prob_preparation)
        self.update_status(self,"Preparation","Action",self.change_prob_action)

        ## Lapse
        self.update_status(self,"Action","Preparation",self.lapse_prob_preparation)
        self.update_status(self,"Preparation","Contemplation",self.lapse_prob_contemplation)
        self.update_status(self,"Contemplation","Pre-contemplation",self.lapse_prob_precontemplation)

        ## Adds one to time
        self.alcohol_status["time"] += 1


    def visit(self,service,probability):
        if self.random.uniform(0,1) <= probability:
            ## randomly selects a service agent
            ServiceAgent_list = [agent for agent in self.model.schedule.agents if isinstance(agent, service)]
            if ServiceAgent_list:
                    visited_service = self.random.choice(ServiceAgent_list)
                    ## runs the chosen service's have contact function
                    visited_service.have_contact(self)


    ## Replaces action to make a visit to a service in base agent
    def move(self,services = [ 'Job Centre'
                              ,'Benefits Office'
                              ,'Housing Officer'
                              ,'Community Hub']):
        
        ## randomises which service is first
        services = self.random.shuffle(services)        
        
        for service in services:
                probability = self.visit_prob[service]
                service = f"{service.replace(" ","")}Agent"
                self.visit(self,service,probability)

                ## updates status after every visit
                self.update_alcohol_status(self)

    ## Defines actions at each step
    def step(self):
        super().step()



