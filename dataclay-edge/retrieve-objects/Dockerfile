FROM bscdataclay/client:dev20210422-alpine
ENV WORKING_DIR=/demo
ARG DC_SHARED_VOLUME=/srv/dataclay/shared
ARG DEFAULT_NAMESPACE=defaultNS
ARG DEFAULT_USER=defaultUser
ARG DEFAULT_PASS=defaultPass
ARG DEFAULT_STUBS_PATH=/demo/stubs
ENV DC_SHARED_VOLUME=${DC_SHARED_VOLUME}  \
    DATACLAYCLIENTCONFIG=${WORKING_DIR}/client.properties  \
    DATACLAYGLOBALCONFIG=${WORKING_DIR}/global.properties   \
    DATACLAYSESSIONCONFIG=${WORKING_DIR}/session.properties \
    NAMESPACE=${DEFAULT_NAMESPACE}  \
    USER=${DEFAULT_USER}  \
    PASS=${DEFAULT_PASS}  \
    STUBSPATH=${DEFAULT_STUBS_PATH}
WORKDIR ${WORKING_DIR}
RUN pip install geolib pygeohash requests
# Copy files
COPY . ${WORKING_DIR}
VOLUME ${DC_SHARED_VOLUME}
ENTRYPOINT ["./dataclay_init.sh"]
CMD ["python", "-u", "./retrieve_objects.py"]
