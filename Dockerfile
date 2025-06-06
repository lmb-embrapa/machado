FROM elasticsearch:7.17.9

RUN mkdir -p /usr/share/elasticsearch/data/nodes && \
    chown -R elasticsearch:elasticsearch /usr/share/elasticsearch/data

USER elasticsearch

COPY --chown=elasticsearch:elasticsearch create_index.sh /usr/local/bin/create_index.sh
RUN chmod +x /usr/local/bin/create_index.sh

CMD ["sh", "-c", "create_index.sh & elasticsearch"]