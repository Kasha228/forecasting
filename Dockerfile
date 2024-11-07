FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY flextools_forecasting/ /app
EXPOSE 5000
RUN chmod +x entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]