# Digital China Internship

## Project Overview

During my internship at Digital China, our team was tasked with building a baseline-management web platform for a client whose multiple departments were struggling with manual document workflows—approvals were getting lost, version control was chaotic, and teams were wasting hours on administrative tasks.

As part of the development team, I worked across the full stack. On the backend, I designed and normalized the relational database schemas in MySQL using MyBatis Plus, ensuring we could handle 20+ concurrent users with transactional consistency and secure CRUD operations. On the frontend, I worked on Vue.js components and integrated them with our backend using Axios for API calls and WebSocket channels for real-time updates—this was crucial for keeping everyone synchronized as documents moved through approval workflows.

I also collaborated closely with our PM throughout the development cycle to refine product specifications, and worked with QA on integration testing to catch issues before deployment.

We successfully deployed the platform to production, reducing their manual processing time by 40%. The system maintained stable uptime post-deployment, which validated our architectural decisions.

## Spring Boot

### 1. Auto-Configuration

"Spring Boot's auto-configuration meant we could deploy a working REST API in under an hour. No XML files, no server installation—just add dependencies and write business logic."

#### Why you chose Spring Boot over Django:

"Our client needed to handle 20+ concurrent users with transactional consistency. Spring Boot's multi-threading and mature transaction management made it better suited for concurrent operations. Additionally, the client's IT team had Java expertise, making maintenance easier."

#### Why you chose Spring Boot over Express.js:

"Spring Boot comes 'batteries included'—security, database connections, transaction management are all built-in. Express.js would require assembling multiple libraries. For an enterprise client managing sensitive document workflows, we needed Spring Boot's mature, battle-tested transaction handling and security features out of the box."

"Spring Boot's annotations made API development fast. The @RestController and @GetMapping annotations automatically handled HTTP routing and JSON serialization. This saved us weeks compared to manual configuration."

### Q: Why Spring Boot instead of plain Spring?

A: "Spring Boot eliminates XML configuration and provides auto-configuration. What took days in plain Spring—setting up database connections, transaction management, web server—took hours in Spring Boot. For a client project with tight deadlines, this was crucial."

### Q: What's the biggest advantage of Spring Boot?

A: "Convention over configuration. Spring Boot makes sensible defaults so you focus on business logic, not infrastructure. For example, just by having MySQL driver in dependencies, Spring Boot automatically configured the connection pool and transaction manager."

### Q: How did Spring Boot help with 20+ concurrent users?

A: "Two ways: First, HikariCP connection pooling (auto-configured) efficiently managed database connections. Second, Spring's @Transactional annotation ensured thread-safe database operations when multiple users submitted documents simultaneously."

## MyBatis Plus

Simple definition: MyBatis Plus is a Java ORM (Object-Relational Mapping) tool that helps you interact with databases without writing repetitive SQL code.

### Why you chose MyBatis Plus over JPA:

"Our approval workflow required complex multi-table JOINs—documents joined with users, departments, approvals, and document types. JPA's auto-generated queries often cause N+1 problems where it executes one query per related record. With 20+ concurrent users, that would kill performance. MyBatis Plus let us write explicit JOIN queries that loaded everything in one database roundtrip."

### Q: Did you write all the SQL yourself?

"For basic operations, MyBatis Plus auto-generated the SQL. But for complex queries—like joining documents with users and departments—we wrote custom SQL in XML files. This gave us full control over performance-critical queries while still avoiding boilerplate for simple operations."

### Q: How did MyBatis Plus connect to your Spring Boot app?

A: "MyBatis Plus has a Spring Boot starter. We added the dependency, configured the database connection in application.properties, and annotated our mapper interfaces with @Mapper. Spring Boot auto-configured everything else—connection pooling, transaction management, mapper scanning."

## Vue.js

Simple definition: Vue.js is a JavaScript framework for building user interfaces. It handles the "view" layer—what users see and interact with in the browser.

### Q1: "What does 'responsive web interface' mean? How did you make it responsive?"

"Responsive means the interface adapts to different screen sizes—desktop, tablet, mobile. We used Element Plus, a Vue UI component library that provides responsive grid layouts. For example, the document list showed 4 columns on desktop but stacked vertically on mobile. We also used CSS flexbox and media queries for custom layouts.

For the document table specifically, on mobile we hid less important columns like 'Created Date' and kept essential ones like 'Title' and 'Status' visible. Users could still access full details by clicking a row."

### Q2: "You mentioned reusable components. Give me an example."

"The best example is our document status badge. It appeared on the document list, document detail page, approval queue, and dashboard—four different places. Instead of duplicating the code, we created a StatusBadge component:

- Input: status string ('draft', 'pending', 'approved', 'rejected')
- Output: colored badge with appropriate styling

```vue
<StatusBadge :status="document.status" />
```

When the client wanted to add a new status 'archived' with gray color, we updated one component file and it worked everywhere. If we had duplicated the code, we'd have to find and update four different places—and probably miss one."

#### Follow-up - "How did you decide what should be a component?"

"I asked myself: 'Will this be used in more than one place?' or 'Is this complex enough to benefit from isolation?'

For example, the entire document form—with title, description, file upload, department selector—became a component because we used it for both creating and editing documents. The form logic stayed the same; we just passed different initial data."

### Q3: "How did you integrate with RESTful APIs?"

"We used Axios as our HTTP client. I created an API service layer that centralized all backend calls."

## MySQL

### Q1: "You mentioned you designed the database schema. Walk me through your design process. What tables did you create?"

I started by identifying the core entities in the document workflow: documents, users, departments, and approvals.

The documents table stores the actual document metadata—title, description, status. But instead of putting all information in one table, I separated users into their own table because multiple documents can be submitted by the same user. Same with departments—many documents belong to one department.

The approvals table was interesting because it's a many-to-many relationship—one document can have multiple approvals, and one user can approve multiple documents. So we created a junction table with document_id and approver_id as foreign keys.

### Q2: "What does 'normalized' mean? Why did you normalize the database?"

"Normalization means breaking data into separate tables to avoid redundancy.

For example, initially I considered putting the department name directly in the documents table. So every document would have 'Engineering' or 'Legal' written in it. But that's a problem—if we rename 'Engineering' to 'Product Engineering', we'd have to update potentially thousands of document records.

Instead, we created a separate departments table with an ID, and documents just reference that ID. Now when a department is renamed, we update one row, not thousands.

We normalized to third normal form, which eliminated these kinds of redundancies and made updates much safer when multiple users are working simultaneously."

### Q3: "You mentioned 20+ concurrent users. What happens if two users try to update the same document at the same time?"

"That's a real issue we had to address. MySQL handles this through transactions and locking.

For example, when a user submits a document for approval, we need to:
1. Update the document's status to 'pending'
2. Create records in the approvals table for each approver

If we don't wrap this in a transaction, and another user is editing the document at the same time, we could end up with the document marked as 'pending' but no approval records created—essentially a corrupted state.

So we used database transactions with the ACID properties. If any part fails, the whole thing rolls back, so when one user is updating a document, other users wait for that transaction to complete before they can modify the same document."

### Q4: "What kind of queries did you write? Can you give me an example?"

**What they're really asking:**

```sql
SELECT 
    d.title,
    d.document_number,
    u.full_name as submitter,
    d.submitted_at
FROM approvals a
JOIN documents d ON a.document_id = d.document_id
JOIN users u ON d.submitter_id = u.user_id
WHERE a.approver_id = ?
  AND a.status = 'pending'
ORDER BY d.submitted_at ASC
```

This joins three tables—approvals, documents, and users—to show all the information needed on the 'pending approvals' dashboard. We filter by the logged-in user's ID and only show pending items. Ordering by submission date shows oldest requests first."

### Q5: "What's a foreign key? Why did you use them?"

"A foreign key is a constraint that links two tables together and enforces referential integrity.

For example, our documents table has a submitter_id column that references the users table. The foreign key constraint means:
1. You can't create a document with submitter_id = 999 if user 999 doesn't exist
2. You can't delete user 999 if they have documents in the system—MySQL will reject the deletion

This was critical for data integrity. During testing, we tried to delete a test user, and MySQL prevented it because they had documents. This protected us from creating 'orphaned' documents with no valid submitter, which would break the approval workflow."

### Q6: "What does 'secure CRUD operations' mean? How did you secure the database?"

"Secure CRUD operations meant two things:

1. **Preventing SQL injection:** We used prepared statements through MyBatis Plus, which automatically escapes user input. So if someone tried entering `'; DROP TABLE users;--` in a document title, it would be treated as literal text, not SQL code.

2. **Role-based access control:** Users had different roles—submitter, approver, manager, admin. At the database level, we enforced this through:
   - Foreign keys ensuring only valid users could create documents
   - Application-level checks before allowing DELETE operations
   - Audit logging—every change tracked who made it and when

We also used database user accounts with minimum necessary privileges. The application didn't connect with the root account—it used a dedicated account that could only access the baseline_management database."

### "How did you measure the 40% reduction in processing time?"

"We tracked timestamps in the database. Every document has a submitted_at and approved_at timestamp. Before the system launched, we recorded the client's average approval time using their manual process—about 50 hours from submission to final approval. After we deployed, we ran a simple query:

```sql
SELECT AVG(TIMESTAMPDIFF(HOUR, submitted_at, approved_at))
FROM documents
WHERE status = 'approved'
  AND submitted_at >= '2023-06-01'  -- Launch date
```

The average dropped to 30 hours, which is a 40% reduction. The timestamps built into the schema made this analysis possible without any extra logging infrastructure. We could also break this down by department or document type to identify bottlenecks."

### Q7: "What was the most challenging database problem you encountered?"

**What they're really asking:**

"During testing, we discovered some documents were stuck in 'pending' status with no approval records. After investigating, I found the issue: when the network was slow, the document update would succeed, but the approval record insertion would timeout and fail.

The fix was wrapping both operations in a transaction. If either failed, both would roll back. This ensured the database stayed consistent even when network issues occurred. This taught me the importance of transactions for multi-step operations."

### Q8: "How did you work with the PM and QA on the database design?"

"The PM didn't need to understand database normalization, but they needed to understand trade-offs.

For example, they wanted to add a 'priority' field to documents. I asked: 'Should priority be freeform text or predefined levels?' They said predefined (low, medium, high, urgent). So I used an ENUM, which enforces those specific values and prevents typos.

With QA, I worked with them on edge cases—like 'what happens if someone tries to delete a user who has approved documents?' We decided to prevent deletion with a foreign key constraint and wrote test cases for it."
