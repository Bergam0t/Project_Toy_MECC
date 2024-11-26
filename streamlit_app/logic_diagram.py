## logic_diagram.py
import schemdraw
from schemdraw import flow

# Set default flowchart box fill colors
flow.Box.defaults['fill'] = '#eeffff'
flow.Start.defaults['fill'] = '#ffeeee'
flow.Decision.defaults['fill'] = '#ffffee'
flow.Circle.defaults['fill'] = '#eeeeee'


#################
## Generic Model
#################
def create_logic_diagram():
    with schemdraw.Drawing() as d:
        
        ## Population
        person = flow.Circle(r=d.unit/2).label('Number of\nPeople').drop("S")
        flow.Arrow().at(person.S).down(d.unit/2)

        m_start = flow.Start().label('Month Start').drop("S")
        
        flow.Arrow().down(d.unit/3).at(m_start.S)
        visit = flow.Decision(S='Visit'
                            ,E='Not Visit').label('Chance visit\na Service').drop("S")
        
        flow.Arrow().down(d.unit/2).at(visit.S)

        with d.container() as service_box:
            service_box.linestyle(":")
            service_box.label("Service",loc="NW",halign="left",valign="top")
            visit_start = flow.Start().label('Visit Start').anchor('N')
            flow.Arrow().down(d.unit/3).at(visit_start.S)
            interv = flow.Decision(W='No\nIntervention'
                                ,S='Intervention').label('Chance Service\nDelivers\nIntervention')
            flow.Arrow().down(d.unit/3).at(interv.S)
            interv_result = flow.Box().anchor('N').label('Person has an\nintervention')
            flow.Arrow().down(d.unit/3).at(interv_result.S)
            visit_end = flow.Start().label('Visit End').anchor('N')
            flow.Wire('c',k=-d.unit/3 ,arrow ='->').at(interv.W).to(visit_end.W)

        flow.Wire('c',arrow ='->').at(visit.E).to(visit_end.E)
        flow.Arrow().down(d.unit/2).at(visit_end.S)

        m_end = flow.Start().label('Month End').drop("E")
        flow.Arrow().right(d.unit/3).at(m_end.E)
        last_m = flow.Decision(E='No'
                            ,S='Yes').label('Is Last Month?').drop("S")
        flow.Arrow().down(d.unit/3).at(last_m.S)
        model_end = flow.Circle(r=d.unit/2).label('Model End')
        flow.Wire('c',k=d.unit/3,arrow ='->').at(last_m.E).to(m_start.E)

    ## Save the drawing to a temporary file
    img_path = "logic_diagram.png"
    d.save(img_path)
    return img_path


#################
## Smoking Model
#################
def create_logic_diagram_SmokeModel():
    with schemdraw.Drawing() as d:
        
        ## Population
        person = flow.Circle(r=d.unit/2).label('Number of\nPeople').drop("S")
        flow.Arrow().at(person.S).down(d.unit/2)

        ## Smokers
        smoke = flow.Decision(E='Not\nSmoker'
                        , W='Smoker').label('Proportion\nof Population\nSmokers').drop("S")
        d.push() ## remembers current location
        flow.Arrow().down(d.unit/2).at(smoke.W)
        is_smoke = flow.Box().label('Smoking Status:\nSmoker').drop("S")
        flow.Arrow().down(d.unit/2).at(smoke.E)

        no_smoke = flow.Box().label('Smoking Status:\nNever Smoked')
        d.pop() ## returns previous remembered location
        d.move(dx=0,dy=-d.unit)

        m_start = flow.Start().label('Month Start').drop("S")
        flow.Wire('n',k=-d.unit/6,arrow ='->').at(is_smoke.S).to(m_start.N)
        flow.Wire('n',k=-d.unit/6,arrow ='->').at(no_smoke.S).to(m_start.N)
        
        flow.Arrow().down(d.unit/3).at(m_start.S)
        visit = flow.Decision(S='Visit'
                            ,E='Not Visit').label('Chance visit\na Service').drop("S")
        
        flow.Arrow().down(d.unit/2).at(visit.S)

        with d.container() as service_box:
            service_box.linestyle(":")
            service_box.label("Service",loc="NW",halign="left",valign="top")
            visit_start = flow.Start().label('Visit Start').anchor('N')
            flow.Arrow().down(d.unit/3).at(visit_start.S)
            interv = flow.Decision(W='No\nIntervention'
                                ,S='Intervention').label('Chance Service\nDelivers\nIntervention')
            flow.Arrow().down(d.unit/3).at(interv.S)
            interv_result = flow.Box().anchor('N').label('Person increases chance\nof making a quit attempt')
            flow.Arrow().down(d.unit/3).at(interv_result.S)
            visit_end = flow.Start().label('Visit End').anchor('N')
            flow.Wire('c',k=-d.unit/3 ,arrow ='->').at(interv.W).to(visit_end.W)

        flow.Wire('c',arrow ='->').at(visit.E).to(visit_end.E)
        flow.Arrow().down(d.unit/2).at(visit_end.S)

        smoke_start = flow.Start().label('Smoking Update Start').anchor('N')
        flow.Arrow().down(d.unit/3).at(smoke_start.S)

        check_smoke = flow.Decision(W='Never\nSmoked'
                                    ,E='Ex-Smoker'
                            ,S='Smoker').label('Is smoker?')
        flow.Arrow().down(d.unit/3).at(check_smoke.S)
        
        quit_attp = flow.Decision(S='No Quit\nAttempt'
                            ,E='Quit\nAttempt').label('Chance Person\nMakes a\nQuit Attempt')
        flow.Arrow().right(d.unit/1.25).at(quit_attp.E)
        quit_result = flow.Box().anchor('W').label('Smoking Status:\nEx-Smoker')
        flow.Arrow().down(d.unit/3).at(quit_result.S)
        restart_smoke = flow.Decision(W='No\nRestart'
                            ,S='Restart\nSmoking').label('Chance Person\nRestarts Smoking')
        flow.Arrow().down(d.unit/3).at(restart_smoke.S)
        restart_result = flow.Box().anchor('N').label('Smoking Status:\nSmoker')
        flow.Arrow().down(d.unit/3).at(restart_result.S)

        smoke_end = flow.Start().label('Smoking Update End').anchor('N')
        flow.Arrow().down(d.unit/3).at(smoke_end.S)
        d.push() ## remembers current location
        flow.Wire('c',k=d.unit*3,arrow ='->').at(check_smoke.E).to(restart_smoke.E) 
        flow.Wire('c',k=-d.unit*1.25,arrow ='->').at(check_smoke.W).to(smoke_end.W)
        flow.Wire('|-',arrow ='->').at(quit_attp.S).to(smoke_end.W)
        flow.Wire('c',k=-d.unit/3,arrow ='->').at(restart_smoke.W).to(smoke_end.W)

        d.pop() ## returns previous remembered location
        m_end = flow.Start().label('Month End').drop("E")
        flow.Arrow().right(d.unit/3).at(m_end.E)
        last_m = flow.Decision(E='No'
                            ,S='Yes').label('Is Last Month?').drop("S")
        flow.Arrow().down(d.unit/3).at(last_m.S)
        model_end = flow.Circle(r=d.unit/2).label('Model End')
        flow.Wire('c',k=d.unit/3,arrow ='->').at(last_m.E).to(m_start.E)

    ## Save the drawing to a temporary file
    img_path = "smoke_logic_diagram.png"
    d.save(img_path)
    return img_path

