Perfect, this is the right place to start.
We’ll treat **Phase 1** like a mini-tutorial with **small tasks + checks** so you don’t get overwhelmed.

We’ll do this in **5 tasks**:

1. Pick region & learn to move around the console
2. Create normal S3 bucket for PDFs
3. Create S3 **vector** bucket + vector index
4. Create an IAM role for Lambdas
5. Create a stub Lambda function and test it

You can do Task 1 now, tell me the results, then we move to Task 2, etc.

---

## 🟦 Task 1 – Set your region & get comfortable in the console

### Why we’re doing this

* **S3 Vectors is only available in certain regions** (like `us-east-1`, `us-east-2`, `us-west-2`, `eu-central-1`, `ap-southeast-2`). ([AWS Documentation][1])
* We want **everything** (S3, S3 Vectors, Lambda, Bedrock later) in **one region**, ideally:

  * `US East (N. Virginia)` → `us-east-1` (safe choice for you in the US).

### Step-by-step (console navigation)

1. **Open AWS Console**

   1. Go to `https://console.aws.amazon.com/`.
   2. Sign in with your AWS account (root or IAM user — for now it’s okay if it’s root since you’re just starting, but long-term we’ll want an IAM user).
2. **Set your region**

   1. Look at the **top-right** of the console.
   2. You’ll see something like `US East (N. Virginia)` or another region name in a dropdown.
   3. Click the dropdown.
   4. Select **US East (N. Virginia)** (`us-east-1`).
3. **Get a feel for the “Services” menu**

   1. At the top, click **“Services”**.
   2. In the search bar there, try typing:

      * `S3`
      * `Lambda`
   3. Just click them once to open, then use the browser **Back** button to go back to the console home.
   4. This is how you’ll navigate most of the time.

### ✅ Checks for Task 1 (tell me after you do these)

* [X] You see `US East (N. Virginia)` in the **top-right** as your chosen region.
* [X] You can:

  * Open **S3** from the Services menu.
  * Open **Lambda** from the Services menu.
* [X] Confirm to me:

  * “Region = us-east-1, I was able to open S3 and Lambda.”

Once you confirm those, we move to Task 2.

---

## 🟦 Task 2 – Create a normal S3 bucket for PDFs (`paper-pdfs`)

### Why we’re doing this

This bucket will store **raw PDFs** that users upload.
Later:

* S3 will trigger **IndexPdfLambda** when a new PDF lands here.

### Step-by-step: Create `paper-pdfs` bucket

1. **Open S3**

   1. From the AWS console home, click **Services → S3**.
   2. You’ll see the S3 dashboard.
2. **Create bucket**

   1. On the top-right, click **“Create bucket”**.
   2. **Bucket name**:

      * Use something like:
        `paper-pdfs-<your-name>-dev`
        Example: `paper-pdfs-rohan-dev`
      * Rules: all lowercase, numbers, and hyphens; must be unique in the region.
   3. **AWS Region**:

      * Make sure it says `US East (N. Virginia) us-east-1`.
   4. **Block Public Access**:

      * Leave the default **“Block all public access”** checked → ✔ (we don’t want PDFs public).
   5. Scroll down, leave everything else as default.
   6. Click **“Create bucket”** at the bottom.
3. **Verify the bucket**

   1. After creation, you should see your bucket in the S3 bucket list.
   2. Click the bucket name.
   3. You’ll see the **Objects** tab (it’ll be empty for now).

### ✅ Checks for Task 2

From the S3 console:

* [X] You can see a bucket named something like `paper-pdfs-<your-name>-dev`.
* [X] When you click into it:

  * The **Objects** tab is visible.
  * Region shown in the bucket details is `US East (N. Virginia)`.

Tell me:

* The **exact bucket name** you used for PDFs.

Then we’ll create the vector bucket.

---

## 🟦 Task 3 – Create S3 **Vector** bucket + Vector Index

Here we’re using S3 **Vectors**: a special kind of bucket that stores and searches embeddings. ([AWS Documentation][2])

### 3.1 Create a S3 **Vector bucket**

#### Why

This is where your **document chunks embeddings** will live. Think of it as your **vector database**.

#### Steps (console)

1. **Open S3** (again, if you’re not already there):

   * Services → S3.
2. **Go to Vector buckets**

   1. On the **left side menu**, under S3, you should see **“Vector buckets”**.
   2. Click **“Vector buckets”**. ([AWS Documentation][2])
3. **Create a vector bucket**

   1. Click **“Create vector bucket”**.
   2. **Vector bucket name**:

      * Use: `paper-vectors-<your-name>-dev`
        Example: `paper-vectors-rohan-dev`
      * Rules: 3–63 chars, lowercase letters, numbers, hyphens only. ([AWS Documentation][2])
   3. **Encryption**:

      * Select **“Server-side encryption with Amazon S3 managed keys (SSE-S3)”**.
        (Default, simplest option).
   4. Leave other options as default.
   5. Click **“Create vector bucket”**.
4. **Verify the vector bucket**

   1. You should now see it listed under **Vector buckets**.
   2. Click its name; this will show its details.

### 3.2 Create a **Vector index** inside this bucket

#### Why

The **index** is where the actual vectors (embeddings) are stored and searched. It needs:

* a **dimension** (how many numbers in each vector),
* the **distance metric** (cosine, euclidean),
* metadata configuration (where we’ll mark `source_text` as non-filterable). ([AWS Documentation][2])

We’ll assume we choose Titan Embeddings at **256 dimensions** for cost + speed; so we’ll set dimension to 256.

#### Steps (console)

1. From **Vector buckets** list, click your vector bucket (`paper-vectors-...`).
2. Inside that bucket, look for a **“Create vector index”** button and click it. ([AWS Documentation][2])
3. Fill in index details:

   1. **Vector index name**:

      * Use: `paper-chunks`
      * Must be 3–63 chars, lowercase, numbers, hyphens/dots. ([AWS Documentation][3])
   2. **Dimension**:

      * Put: `256`
        (we’ll configure Titan embeddings to use 256-dim vectors).
   3. **Data type**:

      * `float32` (that’s what Titan embeddings produce). ([AWS Documentation][4])
   4. **Distance metric**:

      * Choose **cosine** (standard for text embeddings). ([AWS Documentation][4])
   5. **Metadata configuration**:

      * Filterable keys (strings):

        * `user_id`
        * `paper_id`
      * **Non-filterable keys**:

        * `source_text`
          (The console will have fields like “Filterable metadata keys” & “Non-filterable metadata keys.” Add them exactly as text.)
4. Save / Create index.
5. After creation, you should see the index in the bucket’s **Indexes** list.

### ✅ Checks for Task 3

Inside S3 → Vector buckets:

* [X] You can see your vector bucket: `paper-vectors-<your-name>-dev`.
* [X] When you click it, under **Indexes** you see one index called `paper-chunks`.
* [X] For `paper-chunks`, verify:

  * Dimension = `256`
  * Distance metric = `cosine`
  * Filterable metadata keys include `user_id` and `paper_id`
  * Non-filterable metadata keys include `source_text`

Tell me:

* Your **vector bucket name**
* Confirm the index name + dimension + metadata keys.

Then we’ll set up IAM and Lambda.

---

## 🟦 Task 4 – Create an IAM Role for Lambdas

### Why we’re doing this

Every Lambda runs with an **IAM role** that decides what it can access.
We want a role (for now) that can:

* Write logs to **CloudWatch Logs**
* Read from S3 (later buckets)
* Use **Bedrock** and **S3 Vectors** (we’ll tighten later, but we start broad so you can move fast)

We’ll create **one role** now and reuse it for all your phase-1 Lambdas.

### Steps

1. **Open IAM**

   1. From AWS console → **Services → IAM**.
   2. In the left sidebar, click **“Roles”**.
2. **Create a new role**

   1. Click **“Create role”**.
   2. **Trusted entity type**: choose **AWS service**.
   3. **Use case**: select **Lambda**.
   4. Click **Next**.
3. **Attach permissions policies**
   For now (dev only), attach these AWS-managed policies:

   * `AWSLambdaBasicExecutionRole` (for CloudWatch logs)
   * `AmazonS3FullAccess` (we’ll later restrict, but this gets you moving)
   * `AmazonS3VectorsFullAccess` or similarly named S3 Vectors policy if available
   * `AmazonBedrockFullAccess` (for Titan embeddings later)

   Steps:

   1. In the search box, type `AWSLambdaBasicExecutionRole`, check that box.
   2. Type `AmazonS3FullAccess`, check it.
   3. Type `Vectors` or `S3Vectors` – look for **S3 Vectors** related policy (names may be like `AmazonS3VectorsFullAccess` or similar).
   4. Type `Bedrock` – look for `AmazonBedrockFullAccess`, check it.
   5. Click **Next**.
4. **Name the role**

   1. Role name: `rag-lambdas-execution-role`
   2. Click **Create role**.
5. **Verify**

   1. Back on the Roles list, search for `rag-lambdas-execution-role`.
   2. Click it and confirm the attached policies.

### ✅ Checks for Task 4

* [X] In IAM → Roles, you see a role called `rag-lambdas-execution-role` (or your custom name).
* [X] It has at least:

  * `AWSLambdaBasicExecutionRole`
  * `AmazonS3FullAccess`
  * Some S3 Vectors policy
  * Some Bedrock access policy

Tell me:

* The **exact role name** you used.

---

## 🟦 Task 5 – Create a stub Lambda (`IndexPdfLambda`) and test it

We won’t wire S3 triggers yet; just prove that:

* You can create a Lambda in the right region.
* It uses the role we created.
* It runs and logs something.

### Steps

1. **Open Lambda**

   1. Services → **Lambda**.
   2. Make sure in the top-right it still says `US East (N. Virginia)`.
2. **Create function**

   1. Click **“Create function”**.
   2. Choose **Author from scratch**.
   3. Function name: `IndexPdfLambda`.
   4. Runtime: **Python 3.12** (or 3.11, whichever is available).
   5. Permissions:

      * Click **“Change default execution role”**.
      * Choose **“Use an existing role”**.
      * From dropdown, select `rag-lambdas-execution-role`.
   6. Click **“Create function”**.
3. **Add simple test code**

In the function editor, replace the default code with:

```python
import json

def lambda_handler(event, context):
    print("Lambda invoked!")
    print("Event received:", json.dumps(event))
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "IndexPdfLambda is alive"})
    }
```

Click **Deploy** (top-right).

4. **Test it**

   1. Click **Test** (top bar).
   2. It will ask to configure a test event:

      * Event name: `test1`
      * Event template: leave as default JSON or choose “Hello World”.
      * Click **Save**.
   3. Click **Test** again to run it.
5. **Verify execution**

   1. You should see **Execution result: succeeded**.
   2. Response section should show:

      ```json
      {
        "statusCode": 200,
        "body": "{\"message\": \"IndexPdfLambda is alive\"}"
      }
      ```
   3. In the **Logs** section (below), you should see:

      * `Lambda invoked!`
      * `Event received: ...` with the test JSON.

### ✅ Checks for Task 5

* [X] Lambda named `IndexPdfLambda` exists in region `us-east-1`.
* [X] It uses the execution role you created.
* [X] A test invocation succeeded and you saw `IndexPdfLambda is alive` in the response.
* [X] You can see `Lambda invoked!` in the logs output under the test.

---

## What you should do now

1. Work through **Task 1 → 5** in order.
2. After each task, **note down**:

   * Bucket names,
   * Role name,
   * Any errors or confusing screens.
3. Reply to me with:

   * Region,
   * PDF bucket name,
   * Vector bucket + index name + dimension,
   * IAM role name,
   * Whether the test Lambda ran successfully.

Once you send me those results, we’ll move to **Phase 2**, where we’ll:

* Add PDF upload → S3 trigger for `IndexPdfLambda`
* Replace the stub code with real **PDF → text** extraction.

[1]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-regions-quotas.html?utm_source=chatgpt.com
[2]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-getting-started.html?utm_source=chatgpt.com
[3]: https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-indexes.html?utm_source=chatgpt.com
[4]: https://docs.aws.amazon.com/AmazonS3/latest/API/API_S3VectorBuckets_CreateIndex.html?utm_source=chatgpt.com
