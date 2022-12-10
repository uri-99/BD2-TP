# Notilokos

<ol>
    <li>
      <a href="#acerca-del-proyecto">Acerca del proyecto</a>
      <ul>
        <li><a href="#tecnologías-usadas">Tecnologías usadas</a></li>
      </ul>
    </li>
    <li>
        <a href="#instalación">Instalación</a>
            <ul>
                <li><a href="#variables-de-entorno">Variables de entorno</a></li>
                <li><a href="#programas-necesarios">Programas necesarios</a></li>
                <li><a href="#dependencias">Dependencias</a></li>
            </ul>
    </li>
    <li>
        <a href="#uso">Uso</a>
        <ul>
            <li><a href="#autenticación">Autenticación</a></li>
            <li><a href="#permisos">Permisos</a></li>
        </ul>
    </li>
  </ol>



## Acerca del proyecto

Notilokos es un software para el manejo de notas, donde un usuario puede:
- Crear, editar y borrar sus notas. Esto último solo lo puede hacer el dueño de la nota.
- Compartir notas sólo a aquellos que le de permisos, o abrir la nota y que sea leíble o editable por cualquiera.
- Organizar sus notas en carpetas que también puede compartir a quienes quiera.
- Guardar notas de otros como notas favoritas.

Se expone una API para los distintos pedidos del usuario, donde se puede usar el swagger generado para realizar dichos pedidos de una manera más fácil y cómoda.

### Tecnologías usadas

* [![FastAPI][fastapi-logo]][fastapi-url]
* [![MongoDB][mongodb-logo]][mongodb-url]
* [![Elasticsearch][elastic-logo]][elastic-url]
* [![Swagger][swagger-logo]][elastic-url]
* [![JSON Web Tokens][jwt-logo]][jwt-url]

La API del proyecto se hizo usando <a href="https://fastapi.tiangolo.com/">FastAPI</a>, ya que es una tecnología fácil de usar y con mucha documentación disponible para el proceso de desarrollo, desde el primer endpoint local hasta el deploy. A su vez, nos permite generar el <a href="https://swagger.io/">Swagger</a> como documentación y primera interfaz para interactuar con la API.

Por otro lado, para guardar los datos de la aplicación se utilizó la técnica de persistencia políglota, donde se eligieron como bases de datos a usar <a href="https://www.mongodb.com/">FastAPI</a> y <a href="https://www.elastic.co/elasticsearch/">Elasticsearch</a>. La primera, para el guardado de usuarios y carpetas, cuyo formato puede cambiar a futuro, mientras que las notas se guardan en Elasticsearch para agilizar la búsqueda de estas, que es la principal acción que realizarán los usuarios.

Por último, para la autenticación de los usuarios usamos <a href="https://jwt.io/">JSON Web Tokens</a>, o JWT para abreviar, donde un usuario se autentica en primera instancia y se le devuelve un token que usará para autenticarse en los siguientes pedidos.



## Instalación

### Variables de entorno

Por motivos de seguridad, en el código del proyecto no se exponen claves como las usadas para acceder a las bases de datos o generar tokens.

Sin embargo, resulta muy fácil configurarlas, ya que es ubicar un archivo `.env` en el proyecto con las mismas, que conste de:

```js
MONGODB_PASS=<clave_de_mongo>
JWT_KEY=<clave_de_64_bytes>
ELASTIC_USER=<usuario_de_elastic>
ELASTIC_PASSWORD=<contraseña_de_elastic>
ELASTIC_CLASS_ID=<id_de_la_clase>
```

### Programas necesarios

Como prerequisito, se necesita tener instalado python y su sistema de gestión de paquetes pip. Este último se instala con:

```sh
# Descarga del archivo de instalación
$ curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

# Instalación de pip
$ python get-pip.py
```

Luego, para correr el proyecto localmente se necesita de un <a href=https://asgi.readthedocs.io/en/latest/>servidor ASGI</a>. En nuestro caso, usaremos el de <a href="https://www.uvicorn.org/">Uvicorn</a>. Para instalarlo se corre:

```sh
$ pip install uvicorn
```

### Dependencias

Antes de correr el proyecto, hay que instalar una serie de dependencias. Todas se instalan corriendo la siguiente serie de comandos:

```sh
$ pip install pymongo
$ pip install elasticsearch
$ pip install passlib
$ pip install "python-jose[cryptography]"
$ pip install python multipart
$ pip install bcrypt
```



## Uso

Para correr la API localmente se usa el programa Uvicorn antes instalado, de la siguiente manera:

```sh
$ uvicorn main:app --host 127.0.0.1 --port 8000
```

Esto hará que la API corra en la url 127.0.0.1, puerto 8000.

Para acceder al Swagger se deberá dirigir a la url http://127.0.0.1:8000/docs#/, donde estará disponible la documentación de la API y se podrán realizarle pedidos. La interfaz será una parecida a la siguiente:

[![Product Name Screen Shot][product-screenshot]](https://petstore.swagger.io/)

### Autenticación

Para realizar ciertos pedidos se requiere que el usuario esté autenticado, por lo que primero se deberá crear una cuenta mediante un `POST /users` donde estén usuario y contraseña, como se aclara en el Swagger.

Luego, para inciar sesión el usuario deberá mandar un `POST /token` con el usuario y contraseña dentro del body del request, de tipo `x-www-form-encoded`.

Este pedido devolverá un token de tipo <a href=https://jwt.io/>JWT</a>, el cual contiene la información sobre el usuario loggeado y se usará para los pedidos que requieran autenticación, siendo incluido en el header de authorization de la request como:

```sh
Authorization: Bearer <jwt_token>
```

Este token será válido por hasta 30 minutos posterior a su generación, momento en que el usuario debe realizar el `POST /token` nuevamente.

### Permisos

Igualmente, aunque el usuario haya iniciado sesión, hay una serie de acciones que sólo puede realizar si se le otorgaron los permisos necesarios o directamente no puede realizar, a ser:
- Lectura y modificación de archivos que son privados o sólo compartidos a algún grupo de usuarios, en el que no se encuentra el usuario activo.
- Borrado de notas, carpetas y cuentas de otros usuarios.
- Modificaciones de la lista de favoritos de otros usuarios.

[fastapi-logo]: https://img.shields.io/badge/FastAPI-000000?logo=fastapi
[fastapi-url]: https://fastapi.tiangolo.com/
[mongodb-logo]: https://img.shields.io/badge/MongoDB-ffffff?logo=mongodb
[mongodb-url]: https://www.mongodb.com/
[elastic-logo]: https://img.shields.io/badge/Elasticsearch-52a0db?logo=elasticsearch
[elastic-url]: https://www.elastic.co/elasticsearch/
[swagger-logo]: https://img.shields.io/badge/Swagger-808080?logo=swagger
[swagger-url]: https://swagger.io/
[jwt-logo]: https://img.shields.io/badge/JWT-d63aff?logo=jsonwebtokens
[jwt-url]: https://jwt.io/
[product-screenshot]: https://static1.smartbear.co/swagger/media/images/tools/opensource/swagger_ui.png?ext=.png
