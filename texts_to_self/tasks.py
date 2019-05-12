celery = make_celery(app)


@celery.task()
def run_jobs():
    """send sms messages due for current hour"""

    with app.app_context():
        db.init_app(app)

        now = datetime.now()
        print("Current Hour:", now.hour)
        jobs_due = Job.query.filter_by(
            time=str(now.hour) + ':00').all()  # TODO filter out inactive after testing is done

        # jobs_due = session.query(Job).filter_by(time=str(now.hour)+':00').options(joinedload('*')).all()

        print(jobs_due)

        for job in jobs_due:

            print("User:", job.user.username, "User Phone:", job.phone, "User Msg:", job.msg_txt, "Status:", job.active)

            if job.active:
                job_id = job.id
                to = job.phone
                body = job.msg_txt

                send_sms(to, body, job_id)
                # print(to, body, job_id)
                print("Sending:", job.phone, job.msg_txt, job.id)
                # send_sms(job.phone, job.msg_txt, job.id)

        db.session.commit()


CLIENT = Client(env.TWILIO_ACCOUNT_SID, env.TWILIO_AUTH_TOKEN)


@app.route('/outgoing', methods=['GET', 'POST'])
def send_sms(to, body, job_id, from_=env.FROM_PHONE):
    """create sms event"""

    message = CLIENT.messages.create(
        to=to,
        from_=from_,
        body=body
    )

    msg_type = 'outbound'
    job_id = job_id
    msg_sid = message.sid
    user_phone = message.to
    body = message.body
    msg_body = body.replace('Sent from your Twilio trial account - ', '')
    msg_status = message.status

    new_event = Event(
        msg_type=msg_type,
        job_id=job_id,
        msg_sid=msg_sid,
        user_phone=user_phone,
        msg_body=msg_body,
        msg_status=msg_status
    )

    db.session.add(new_event)


@app.route("/incoming", methods=['GET', 'POST'])
def receive_reply():
    """Respond to incoming messages with a friendly SMS."""

    job = Job.query.filter_by(phone=request.values.get('From')).first()

    msg_type = 'inbound'
    job_id = job.id
    msg_sid = request.values.get('MessageSid')
    user_phone = request.values.get('From')
    msg_body = request.values.get('Body')
    msg_status = request.values.get('SmsStatus')

    new_reply = Event(
        msg_type=msg_type,
        job_id=job_id,
        msg_sid=msg_sid,
        user_phone=user_phone,
        msg_body=msg_body,
        msg_status=msg_status
    )

    db.session.add(new_reply)
    db.session.commit()

    resp = MessagingResponse()
    resp.message("Your response has been logged.")

    print(resp)

    return str(resp)
