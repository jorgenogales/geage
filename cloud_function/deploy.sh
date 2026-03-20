gcloud functions deploy generate-exception-function \
   --gen2 \
   --runtime=python311 \
   --region=us-central1 \
   --source=. \
   --entry-point=generate_exception \
   --trigger-http \
   --allow-unauthenticated
