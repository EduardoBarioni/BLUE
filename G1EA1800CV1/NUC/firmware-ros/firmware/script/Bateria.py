#!/usr/bin/env python

import rospy
from std_msgs.msg import Float64
from std_msgs.msg import Int16
import Database

#Constantes
SIZE_VET_BAT = 20
STEP_AD_3V3_NORMALIZADO = 3222
STEP_AD_5V0_NORMALIZADO = 4882
STEP_AD_NORMALIZADO = STEP_AD_3V3_NORMALIZADO
GANHO_NORMALIZADO = 182
TENSAO_REFERENCIA_NORMALIZADA = 125000
DIVISOR_RESISTIVO_NORMALIZADO = 16151


#Valor atual da bateria
tensaoBateria = 52000 #Valor inicial


#Usado na media movel
tensao_valores = [0]*SIZE_VET_BAT
pos_bat = 0


#Publishers para publicar nivel de bateria
pub_bateria= rospy.Publisher("bateria", Float64, queue_size=10)


def bateria_callback(valor_bateria):
	global tensaoBateria
	global pos_bat
	global tensao_valores
	
	if (pos_bat >= SIZE_VET_BAT):
		pos_bat = 0

	aux = valor_bateria.data * STEP_AD_NORMALIZADO
	aux = aux * GANHO_NORMALIZADO
	aux = aux / 10000
	aux = aux + TENSAO_REFERENCIA_NORMALIZADA
	aux = aux * DIVISOR_RESISTIVO_NORMALIZADO
	aux = aux / 100000

	tensao_valores[pos_bat] = aux #* 1.07

	val = 0
	for valor in tensao_valores:
		val = valor + val

	tensaoBateria = val / SIZE_VET_BAT #* 1.81 * 0.71 * 1.35
	pos_bat = pos_bat + 1


if __name__ == '__main__':
    rospy.init_node('Bateria', anonymous=False)
    rospy.Subscriber("agv_p106", Int16, bateria_callback, queue_size=1, buff_size=2**24)

    rate = rospy.Rate(1) #1Hz --> 1 vez por segundo
    while not rospy.is_shutdown():
        pub_bateria.publish(tensaoBateria)
        rate.sleep()
