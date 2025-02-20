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
from model_two_types_mecc import (PersonAgent
                                  , ServiceAgent
                                  , MECC_Model
                                  , calculate_total_interventions
                                  , calculate_total_contacts)


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
                service = f"{service.replace(' ','')}Agent"
                self.visit(self,service,probability)
                

    ## Defines actions at each step
    def step(self):
        super().step()
        self.update_alcohol_status(self)


##################################
### Service Agent Class
##################################

## creates a subclass of service agent for alcohol model
class AlcoholModel_ServiceAgent(ServiceAgent):
    def __init__(self
                 , unique_id
                 , model
                 , mecc_effect
                 , base_make_intervention_prob
                 , mecc_trained
                 , contemplation_intervention
                 , preparation_intervention
                 , action_intervention
                 , category
                 ,):
        super().__init__(unique_id, model
                         , mecc_effect
                         , base_make_intervention_prob
                         , mecc_trained)

        ## Assign
        self.category = category

        ## Intervention Effect
        self.contemplation_intervention = contemplation_intervention
        self.preparation_intervention = preparation_intervention
        self.action_intervention = action_intervention

    @classmethod
    def describe(cls):
        """Class method to print class information."""
        print(f"This is a service agent of the category {cls.category}")

    ## Override to perform alcohol-specific interventions
    def perform_intervention(self, PersonAgent):
        PersonAgent.change_prob_contemplation += self.contemplation_intervention
        PersonAgent.change_prob_preparation += self.preparation_intervention
        PersonAgent.change_prob_action += self.action_intervention

    ## doesn't do anything at each step
    def step(self):
        pass


services_list = [ 'Job Centre'
            ,'Benefits Office'
            ,'Housing Officer'
            ,'Community Hub']

# Dictionary to store the dynamically created classes
Alcohol_Services = {}

for service in services_list:
    service_agent = f"{service.replace(' ','')}Agent"
    new_class = type(service_agent
                     ,(AlcoholModel_ServiceAgent,)
                     ,{"category":service})
    Alcohol_Services[service_agent] = new_class




##################################
### Model Class
##################################

## creates a subclass of model for alcohol
class Alcohol_MECC_Model(MECC_Model): 
    def __init__(self
                , N_people
                #, N_service
                , seed

                ## dictionaries of intervention chance
                 , contemplation_intervention
                 , preparation_intervention
                 , action_intervention

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

                ## site properties
                , mecc_effect = {}
                , base_make_intervention_prob = {}
                , mecc_trained = {}         
                ):
        super().__init__( N_people
                #, N_service
                , mecc_effect
                , base_make_intervention_prob 
                #, visit_prob
                , mecc_trained     
                , seed )  # Properly initialize the MECC_Model class

        self.services_list = [ 'Job Centre'
                    ,'Benefits Office'
                    ,'Housing Officer'
                    ,'Community Hub']
        
        ## Convert dictionary values if they're dictionaries
        def extract_value(data):
            """Extract 'value' key if data is a dictionary, otherwise return data as is."""
            return data['value'] if isinstance(data, dict) else data

        ## alcohol features for person agents
        self.change_prob_contemplation   = extract_value(change_prob_contemplation)
        self.change_prob_preparation     = extract_value(change_prob_preparation)
        self.change_prob_action          = extract_value(change_prob_action)

        self.lapse_prob_precontemplation = extract_value(lapse_prob_precontemplation)
        self.lapse_prob_contemplation    = extract_value(lapse_prob_contemplation)
        self.lapse_prob_preparation      = extract_value(lapse_prob_preparation) 

        self.visit_prob_Job_centre      = extract_value(visit_prob_Job_centre)
        self.visit_prob_Benefits_office = extract_value(visit_prob_Benefits_office)
        self.visit_prob_Housing_officer = extract_value(visit_prob_Housing_officer)
        self.visit_prob_Community_hub   = extract_value(visit_prob_Community_hub)

        ## Overwrite base properties with dict versions
        self.mecc_effect = mecc_effect
        self.base_make_intervention_prob = base_make_intervention_prob
        self.mecc_trained = mecc_trained

        ## site intervention chance
        self.contemplation_intervention = contemplation_intervention
        self.preparation_intervention = preparation_intervention
        self.action_intervention = action_intervention

        ## Overwrite Data collector for metrics
        self.datacollector = DataCollector(
            model_reporters={
                "Total Contacts": calculate_total_contacts,
                "Total Interventions": calculate_total_interventions,
                "Total Pre-contemplation":  calculate_number_status_precontemplation,
                "Total Contemplation":  calculate_number_status_contemplation,
                "Total Preparation":  calculate_number_status_preparation,
                "Total Action":  calculate_number_status_action,
                "Job Centre Interventions": calculate_service_interventions_JobCentre,
                "Benefits Office Interventions": calculate_service_interventions_BenefitsOffice,
                "Housing Officer Interventions": calculate_service_interventions_HousingOfficer,
                "Community Hub Interventions": calculate_service_interventions_CommunityHub,
                "Job Centre Contacts": calculate_service_contacts_JobCentre,
                "Benefits Office Contacts": calculate_service_contacts_BenefitsOffice,
                "Housing Officer Contacts": calculate_service_contacts_HousingOfficer,
                "Community Hub Contacts": calculate_service_contacts_CommunityHub,
            },
            agent_reporters={}
        )
        
        ## Reset Schedule to overwrite for agents
        self.schedule = RandomActivation(self)

        ## Create person agents
        for i in range(self.N_people):
            a = AlcoholModel_PersonAgent(unique_id = i
                            , model = self
                            ## demographics
                            , gender = None
                            , age = None
                            , deprivation = None

                            ## change state probability
                            , change_prob_contemplation = self.change_prob_contemplation
                            , change_prob_preparation = self.change_prob_preparation
                            , change_prob_action = self.change_prob_action

                            , lapse_prob_precontemplation = self.lapse_prob_precontemplation
                            , lapse_prob_contemplation = self.lapse_prob_contemplation
                            , lapse_prob_preparation = self.lapse_prob_preparation

                            ## visit probability
                            , visit_prob_Job_centre = self.visit_prob_Job_centre
                            , visit_prob_Benefits_office = self.visit_prob_Benefits_office
                            , visit_prob_Housing_officer = self.visit_prob_Housing_officer
                            , visit_prob_Community_hub = self.visit_prob_Community_hub
                            )
            self.schedule.add(a)

        ## Create service agents
        for i, service in enumerate(self.services_list,start=1):
            service_agent = f"{service.replace(' ','')}Agent"

            a = Alcohol_Services[service_agent](unique_id = i + self.N_people
                    , model = self

                    , mecc_effect = self.mecc_effect[service]
                    , base_make_intervention_prob  = self.base_make_intervention_prob[service]
                    , mecc_trained = self.mecc_trained[service]
                    , contemplation_intervention = self.contemplation_intervention[service]
                    , preparation_intervention = self.preparation_intervention[service]
                    , action_intervention = self.action_intervention[service]
                    )
        
            self.schedule.add(a)

##################################
### Metric Outputs
##################################

## number of people with a given alcohol status
def calculate_number_status(model,status):
    return sum(1 for agent in model.schedule.agents 
              if isinstance(agent, AlcoholModel_PersonAgent)
                and agent.alcohol_status["status"] == status)

def calculate_number_status_precontemplation(model):
    calculate_number_status(model,"Pre-contemplation")

def calculate_number_status_contemplation(model):
    calculate_number_status(model,"Contemplation")

def calculate_number_status_preparation(model):
    calculate_number_status(model,"Preparation")

def calculate_number_status_action(model):
    calculate_number_status(model,"Action")

## number of interventions by a service type
def calculate_service_interventions(model,service):
    return sum(agent.interventions_made for agent in model.schedule.agents 
              if isinstance(agent, AlcoholModel_ServiceAgent)
                and agent.category == service)

def calculate_service_interventions_JobCentre(model): 
    calculate_service_interventions(model,"Job Centre")

def calculate_service_interventions_BenefitsOffice(model):
    calculate_service_interventions(model,"Benefits Office")

def calculate_service_interventions_HousingOfficer(model): 
    calculate_service_interventions(model,"Housing Officer")
 
def calculate_service_interventions_CommunityHub(model):
    calculate_service_interventions(model,"Community Hub")

## number of contacts by a service type
def calculate_service_contacts(model,service):
    return sum(agent.contacts_made for agent in model.schedule.agents 
              if isinstance(agent, AlcoholModel_ServiceAgent)
                and agent.category == service)

def calculate_service_contacts_JobCentre(model): 
    calculate_service_contacts(model,"Job Centre")

def calculate_service_contacts_BenefitsOffice(model):
    calculate_service_contacts(model,"Benefits Office")

def calculate_service_contacts_HousingOfficer(model): 
    calculate_service_contacts(model,"Housing Officer")
 
def calculate_service_contacts_CommunityHub(model):
    calculate_service_contacts(model,"Community Hub")
