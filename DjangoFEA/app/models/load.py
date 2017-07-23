from django.db import models
import numpy as np
import math as math
from app.models import DataItem, Node, Element

class Load(DataItem):
    #type = models.IntegerField()
    associated_element = models.ForeignKey(Element, on_delete=models.CASCADE, unique=False)
    f1 = models.FloatField()
    coord1 = models.FloatField()
    m = models.FloatField()
    deg = models.FloatField()

class ConcentratedLoad(Load):
    def __str__(self):
        return "conc"

    #static boundary conditions
    '''the function acts as follows:
        1. read nodes, bar data etc.,
        2. in case of concentrated load, basing on element type
            (fixed-fixed etc.), apply load to global force matrix,
        3. in case of distributed load, first check if distX or distY
            and set appropriate values of angles and loads,
        4. fill po matrix with values.
        '''

    def bc(self, po):
        x1 = self.associated_element.node_start.x
        y1 = self.associated_element.node_start.y
        x2 = self.associated_element.node_end.x
        y2 = self.associated_element.node_end.y      
        L = math.sqrt ((x2 - x1) **2 + (y2 - y1) **2)
        angle = self.deg*math.pi/180
            
        node_a = list(Node.objects.all()).index(self.associated_element.node_start)
        node_b = list(Node.objects.all()).index(self.associated_element.node_end)
        bc0 = self.associated_element.hinge_start
        bc1 = self.associated_element.hinge_end
                  
        sin_loc = math.sin(angle)
        cos_loc = math.cos(angle)
        sin = (y2-y1) / L
        cos = (x2-x1) / L 
   
        p = self.f1
        Mz = self.m
        b = self.coord1*L
        a = L-b
        if bc0 == False and bc1 == False:
            #concentrated force part
            po[node_a*3] += sin*(-p*cos_loc*(a**2)*(L+2*b))/(L ** 3) - a/L*p*sin_loc*cos
            po[node_a*3+1] += -cos*(-p*cos_loc*(a**2)*(L+2*b))/(L ** 3) - a/L*p*sin_loc*sin
            po[node_a*3+2] += cos_loc*p*b*(a ** 2)/(L ** 2)
            po[node_b*3] += (-sin*p*cos_loc*(b**2)*(L+2*a))/(L ** 3) - b/L*p*sin_loc*cos
            po[node_b*3+1] += -cos*(-p*cos_loc*(b**2)*(L+2*a))/(L ** 3) - b/L*p*sin_loc*sin
            po[node_b*3+2] += -cos_loc*p*a*(b ** 2)/(L ** 2) 
            #concentrated moment part
            po[node_a*3] += sin*(6*Mz*a)/L**3*(L-a)
            po[node_a*3+1] += -cos*(6*Mz*a)/L**3*(L-a)
            po[node_a*3+2] += Mz/L**2*(3*a**2-2*a*L)
            po[node_b*3] += -sin*(6*Mz*a)/L**3*(L-a)
            po[node_b*3+1] += cos*(6*Mz*a)/L**3*(L-a)
            po[node_b*3+2] += Mz/L**2*(L**2-4*a*L+3*a**2)
        elif bc0 == False and bc1 == True:
            #concentrated force part
            po[node_a*3] += sin*(-p*cos_loc*a*(3-(a/L)**2)/(2*L)) - a/L*p*sin_loc*cos
            po[node_a*3+1] += -cos*(-p*cos_loc*a*(3-(a/L)**2)/(2*L)) - a/L*p*sin_loc*sin
            po[node_a*3+2] += cos_loc*p*0.5*b*a*(2-b/L)/L
            po[node_b*3] += sin*(-p*cos_loc*(b**2)*(3-b/L))/(L ** 2)/2 - b/L*p*sin_loc*cos
            po[node_b*3+1] += -cos*(-p*cos_loc*(b**2)*(3-b/L))/(L ** 2)/2 - b/L*p*sin_loc*sin
            po[node_b*3+2] += 0
            #concentrated moment part
            po[node_a*3] += sin*3*Mz/2/L*(1-a**2/L**2)
            po[node_a*3+1] += -cos*3/2*Mz/L*(1-a**2/L**2)
            po[node_a*3+2] += -Mz/2*(1-3*a**2/L**2)
            po[node_b*3] += -sin*3/2*Mz/L*(1-a**2/L**2)
            po[node_b*3+1] += cos*3/2*Mz/L*(1-a**2/L**2)
            po[node_b*3+2] += 0
        elif bc0 == True and bc1 == False:
            #concentrated force part
            po[node_a*3] += sin*(-p*cos_loc*(a**2)*(3-a/L))/(L ** 2)/2 - a/L*p*sin_loc*cos
            po[node_a*3+1] += -cos*(-p*cos_loc*(a**2)*(3-a/L))/(L ** 2)/2 - a/L*p*sin_loc*sin
            po[node_a*3+2] += 0
            po[node_b*3] += sin*(-p*cos_loc*b*(3-(b/L)**2)/(2*L)) - b/L*p*sin_loc*cos
            po[node_b*3+1] += -cos*(-p*cos_loc*b*(3-(b/L)**2)/(2*L)) - b/L*p*sin_loc*sin
            po[node_b*3+2] += -p*cos_loc*0.5*b*a*(2-a/L)/L
            #concentrated moment part
            po[node_a*3] += sin*3*Mz/2/L*(1-b**2/L**2)
            po[node_a*3+1] += -cos*3/2*Mz/L*(1-b**2/L**2)
            po[node_a*3+2] += 0
            po[node_b*3] += -sin*3/2*Mz/L*(1-b**2/L**2)
            po[node_b*3+1] += cos*3/2*Mz/L*(1-b**2/L**2)
            po[node_b*3+2] += -Mz/2*(1-3*b**2/L**2)
        else:
            #concentrated force part
            po[node_a*3] += sin*(-p*cos_loc*a/L) - a/L*p*sin_loc*cos
            po[node_a*3+1] += -cos*(-p*cos_loc*a/L) - a/L*p*sin_loc*sin
            po[node_a*3+2] += 0
            po[node_b*3] += sin*(-p*cos_loc*b/L) - b/L*p*sin_loc*cos
            po[node_b*3+1] += -cos*(-p*cos_loc*b/L) - b/L*p*sin_loc*sin
            po[node_b*3+2] += 0
            #concentrated moment part
            po[node_a*3] += sin*Mz/L
            po[node_a*3+1] += -cos*Mz/L
            po[node_a*3+2] += 0
            po[node_b*3] += -sin*Mz/L
            po[node_b*3+1] += cos*Mz/L
            po[node_b*3+2] += 0

        return po


    def dis_loads(self, i):
        num_of_calc = 100

        #initial data
        item = self.associated_element
        x1 = self.associated_element.node_start.x
        y1 = self.associated_element.node_start.y
        x2 = self.associated_element.node_end.x
        y2 = self.associated_element.node_end.y      
        L = math.sqrt ((x2 - x1) **2 + (y2 - y1) **2)

        bc0 = self.associated_element.hinge_start
        bc1 = self.associated_element.hinge_end

        E = self.associated_element.section.E*100000000
        A = self.associated_element.section.A/10000
        J = self.associated_element.section.J/100000000

        zeta = i/L
            
        #displacements for clamped beam
        dy_cl = 0
        dy_hin = 0

        angle = self.deg*math.pi/180                   
        F = math.cos(angle)*self.f1  
        Mz = self.m
        a = self.coord1*L                                   
        b = L-a   
        if i <= a:
            #concentrated force
            dy_cl += - F / (6*E*J) * ((b**2) * (i**3) * (L+2*a) / (L**3) - 3*a*(b**2)*(i**2) / (L**2))
            #concentrated moment
            dy_cl += 1/(2*E*J)*(Mz/L**2*(3*b**2-2*b*L)*i**2+(6*Mz*b)/L**3*(L-b)*i**3/3)
        else:
            #concentrated force
            dy_cl += - F / (6*E*J) * ((b**2) * (i**3) * (L+2*a) / (L**3) - 3*a*(b**2)*(i**2) / (L**2) - ((i-a)**3))
            #concentrated moment
            dy_cl += 1/(2*E*J)*(Mz/L**2*(3*b**2-2*b*L)*i**2+(6*Mz*b)/L**3*(L-b)*i**3/3)-Mz/(2*E*J)*(i-a)**2
        #in case load on bar with hinges
        if bc0 == False and bc1 == True:
            #concentrated force
            V5 = L*(-(zeta**2)+(zeta**3))
            v_add = -math.cos(loads.angle_var.get()*math.pi/180)*loads.F_var.get()*(L**2)*(loads.coord_var.get()**2)*(1-loads.coord_var.get())/(4*E*J)
            dy_hin += v_add*V5
            #concentrated moment
            v_add = -Mz/(E*J)*(b-L/4-3/4*b**2/L)
            dy_hin += v_add*V5
        elif bc0 == True and bc1 == False:
            V5 = L*(zeta-2*(zeta**2)+(zeta**3))
            #concentrated force
            v_add = math.cos(loads.angle_var.get()*math.pi/180)*loads.F_var.get()*(L**2)*loads.coord_var.get()*(1-loads.coord_var.get())**2/(4*E*J)
            dy_hin += v_add*V5
            #concentrated moment
            v_add = -Mz/(E*J)*(a-L/4-3/4*a**2/L)
            dy_hin += v_add*V5
        elif bc0 == True and bc1 == True:
            #concentrated force
            V5 = L*(zeta-2*(zeta**2)+(zeta**3))
            v_add = math.cos(loads.angle_var.get()*math.pi/180)*loads.F_var.get()*b*(L**2-b**2)/(6*L*E*J)
            dy_hin += v_add*V5
            v_add = math.cos(loads.angle_var.get()*math.pi/180)*loads.F_var.get()*a*b*(2*L-b)/(6*L*E*J)
            V5 = L*(-(zeta**2)+(zeta**3))
            dy_hin += -v_add*V5
            #concentrated moment
            V5 = L*(zeta-2*(zeta**2)+(zeta**3))
            v_add = Mz/(6*E*J)*(2*L-6*a+3*a**2/L)
            dy_hin += v_add*V5
            v_add = Mz/(6*E*J)*(L-3*a**2/L)
            V5 = L*(-(zeta**2)+(zeta**3))
            dy_hin += -v_add*V5
            
        #axial displacement for axial tension
        dx_cl = 0

        Fx = math.sin(angle)*self.f1
        if i <= a:
            dx_cl += - Fx*i*(L-a)/L/(E*A)
        else:
            dx_cl += Fx*(i-L)*a/L/(E*A)
            
        return dx_cl, dy_cl + dy_hin  


class DistributedLoad(Load):
    def __str__(self):
        return "distr"

    def abc(self):
        return 3

class DistributedXLoad(Load):
    def __str__(self):
        return "distr-X"

    def abc(self):
        return 3
