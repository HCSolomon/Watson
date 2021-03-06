import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.gson.Gson;
import io.kubernetes.client.ApiException;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Properties;

public class SherlockRetrain extends SherlockBase {
    public SherlockRetrain(String ip, String port, String bucket, String model_pref, String model_name) throws IOException, ApiException {
        super(ip, port, bucket, model_pref, model_name);
    }

    public void retrain(String url, String bucket) throws IOException {
        String json = "";
        try {
            URL client = new URL(url);
            HttpURLConnection connection = (HttpURLConnection) client.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("epochs", "5");
            connection.setRequestProperty("batch_size", "30");
            connection.setRequestProperty("bucket_name", bucket);
            connection.setRequestProperty("bucket_prefix", getModelPrefix());
            connection.setRequestProperty("model_name", getModelName());

            if (connection.getResponseCode() == 200) {
                BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                String line = null;
                StringBuilder stringBuilder = new StringBuilder();
                while ((line = reader.readLine()) != null) {
                    stringBuilder.append(line + "\n");
                }
                json = stringBuilder.toString();
            }
            else {
                System.out.println("Error: Response code " + connection.getResponseCode());
            }
        } catch (MalformedURLException e) {
            e.printStackTrace();

        } catch (IOException e) {
            e.printStackTrace();
        }

        HashMap<String, Object> msg = new ObjectMapper().readValue(json, HashMap.class);
        HashMap<String, Object> status = new ObjectMapper().readValue(msg.get("msg").toString(), HashMap.class);
        if (msg.get("status") == "SUCCESS") {
            Properties props = new Properties();
            props.put("bootstrap.servers", Paths.get(getIP(), ":", getPort()).toString());
            props.put("transactional.id", "t-id");
            Producer<String, String> producer = new KafkaProducer<String, String>(props, new StringSerializer(), new StringSerializer());
            String result = new Gson().toJson(msg.get("result"));

            producer.initTransactions();

            producer.send(new ProducerRecord<String, String>("postgres_models", result));
        }
    }
}
