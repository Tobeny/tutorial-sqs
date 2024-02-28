import time
from flask import Flask, request,jsonify
import boto3
import threading

app = Flask(__name__)

# Configura el cliente de SQS
sqs = boto3.client('sqs', region_name='us-east-2')

@app.route('/health')
def health_check():
    # Aquí podrías realizar algunas verificaciones para determinar
    # el estado de salud de tu aplicación
    # Por ejemplo, podrías verificar la conexión a una base de datos,
    # la disponibilidad de servicios externos, etc.

    # Si todas las comprobaciones son exitosas, devuelve un mensaje de estado OK
    return jsonify({'status': 'ok'})


# Ruta para enviar mensajes a la cola de SQS
@app.route('/enviar-mensaje', methods=['POST'])
def enviar_mensaje():
    mensaje = request.json['mensaje']
    cola_url = 'https://sqs.us-east-2.amazonaws.com/038172446204/sqssportapp'

    # Envía el mensaje a la cola de SQS
    response = sqs.send_message(
        QueueUrl=cola_url,
        MessageBody=mensaje
    )

    return 'Mensaje enviado a la cola de SQS'

# Ruta para recibir mensajes de la cola de SQS en un hilo
@app.route('/recibir-mensaje', methods=['GET'])
def recibir_mensaje():
    cola_url = 'https://sqs.us-east-2.amazonaws.com/038172446204/sqssportapp'

    # Función para recibir mensajes en un hilo
    def recibir_mensajes():
        while True:
            response = sqs.receive_message(
                QueueUrl=cola_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20
            )

            if 'Messages' in response:
                for message in response['Messages']:
                    # Procesa el mensaje recibido
                    print('Mensaje recibido:', message['Body'])

                    # Elimina el mensaje de la cola
                    sqs.delete_message(
                        QueueUrl=cola_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )
            time.sleep(5)

    # Inicia el hilo para recibir mensajes
    thread = threading.Thread(target=recibir_mensajes)
    thread.start()

    return 'Hilo de recepción de mensajes iniciado'

@app.route('/')
def index():
    return "¡Hola desde Flask dentro de Docker!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
