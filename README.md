# Job-Internship-system
Python flask based application- Helps employer and job seeker for employment.
Companies and HR managers can put on the vacant posts and positions.
Job seekers can upload their resume and see if they are fit for the required post.
It also finds available jobs matching your resume.
An AI textbox where one can ask about loopholes in their resume.<br>
 ## Tools Used
  - Python Flask
  - Flask sql_alchemy
  - Jinga (templating Language, which allow us to write some python logic inside of html)
  - Front_end Language (HTML, CSS styles, JS bootstraps)

## Structure of the project
```bash
  .
  |- website/
  |  |-resumes
  |  ⨽templates/
  |    |-application_status.html
  |    ⨽apply_job.html
  |    ⨽base.html
  |    ⨽general_apply.html
  |    ⨽home.html
  |    ⨽login.html
  |    ⨽post_job.html
  |    ⨽sign_up.html
  |    ⨽view_general_applications.html
  |    ⨽view_job_applications.html
  |  |-_init_.py
  |  ⨽auth.py
  |  ⨽models.py
  |  ⨽views.py
  |-main.py

```
## Running the app
```bash
  python main.py
```
