TEST_LOG_FILE="test-results-$(date +%Y%m%d-%H%M%S).log"

export API_URL="https://vgbcvffl73.execute-api.us-east-1.amazonaws.com/dev"
export CUSTOMER_DATA_TABLE="multi-tenant-api-customer-data"
export REGION="us-east-1"
export RANDOM_ID=10
export TEST_CUSTOMER_ID="test-customer-$RANDOM_ID"
export TEST_CUSTOMER_NAME="Test Customer-name-$RANDOM_ID"

export ADMIN_API_KEY="}GU1*0$)N'Ure=#C?JrkMHyk.F^*KH8,"


# Admin Operations
# Create a new customer

curl -X POST "$API_URL/admin/keys" -H "Content-Type: application/json" -H "X-Admin-API-Key: $ADMIN_API_KEY" -d "{\"customer_id\":\"$TEST_CUSTOMER_ID\",\"customer_name\":\"$TEST_CUSTOMER_NAME\"}"
# {"api_key": "YAHA3DePs-MOPpMq3_xZG8lUYeT3SSm8fTFz3sczXVk", "customer_id": "test-customer-1", "message": "API key created successfully"} 

# Post Data for a customer using Admin Keys (You can also use Utility service to post data using Excle sheet - https://github.com/amit-ecovoice/C-dazpak/tree/main/customer-secure-api/utility)
curl -X PUT "$API_URL/admin/upsert" -H "X-Admin-API-Key: $ADMIN_API_KEY" -H "Content-Type: application/json" -d '{"customer_id": "Calyx Containers", "data_id": "SO001-001", "data": {"name": "Product Name","value": 100,"SONum": "SO001","SOLine": "001"}}'

curl -X DELETE "$API_URL/admin/keys/$TEST_CUSTOMER_ID" -H "Content-Type: application/json"
{"message": "API key for customer test-customer-3 revoked"}




# Customer Operations
# Get the JWT token
curl -X POST "$API_URL/auth" -H "Content-Type: application/json" -d "{\"api_key\":\"J4-nC1ggiCs4s--OW3qRgQSwVCbaLMm2G2VnH2mNQQI\"}"

# Set TOKEN as Variable
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjdXN0b21lcl9pZCI6InRlc3QtY3VzdG9tZXItMTAiLCJleHAiOjE3NTQzNDEyMDMsImlhdCI6MTc1NDMzNzYwM30.U0MwIB_lcMqxRizJ5eNbkRdbiS0vgIdu_8HVP3gE-0I"
              

curl -s -X GET "$API_URL/data" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json"
{"customer_id": "test-customer-1", "data": [{"customer_id": "test-customer-1", "value": 10.0, "data_id": "sample-data-1", "created_at": "2025-08-04T18:44:46Z", "name": "Sample Data Item 1"}], "count": 1}

curl -s -X GET "$API_URL/data?limit=2" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" 
{"customer_id": "test-customer-1", "data": [{"customer_id": "test-customer-1", "value": 10.0, "data_id": "sample-data-1", "created_at": "2025-08-04T18:44:46Z", "name": "Sample Data Item 1"}, {"customer_id": "test-customer-1", "value": 20.0, "data_id": "sample-data-2", "created_at": "2025-08-04T18:51:31Z", "name": "Sample Data Item 2"}], "count": 2, "nextToken": "eyJjdXN0b21lcl9pZCI6ICJ0ZXN0LWN1c3RvbWVyLTEiLCAiZGF0YV9pZCI6ICJzYW1wbGUtZGF0YS0yIn0="}

export NEXT_PAGE_TOKEN="eyJjdXN0b21lcl9pZCI6ICJ0ZXN0LWN1c3RvbWVyLTEiLCAiZGF0YV9pZCI6ICJzYW1wbGUtZGF0YS0yIn0="

curl -s -X GET "$API_URL/data?limit=3&nextToken=$NEXT_PAGE_TOKEN" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json"
{"customer_id": "test-customer-1", "data": [{"customer_id": "test-customer-1", "value": 30.0, "data_id": "sample-data-3", "created_at": "2025-08-04T18:52:05Z", "name": "Sample Data Item 3"}], "count": 1}


