# coding=UTF-8
from django import forms
from django.shortcuts import redirect
from trybar.core import render, gpinfo
from datetime import datetime, timedelta
from datetime import datetime
from hashlib import sha1
from django.http import HttpResponse
from django.template import Template, Context
from django.http import Http404
from trybar.account import must_be_logged, standard_profile_page_dict
from trybar.account.models import Account, Familiar, AccountPhoto, AccountPhotoComment
from trybar.main.models import News
from trybar.scoring import score_for, ACCOUNT_PHOTO_ADDED, ranking_dirty, ACCOUNT_PHOTO_COMMENT_ADDED
from trybar.accnews import accnews_for, RT_PRIVPHOTO_ADDED, RT_COMMENT_PRIVGAL
from trybar.photo.upload import upload_as, RES_ACCOUNT_PHOTO

DEFAULT_COMMENT_TEXT = u'Tutaj wpiść treść komentarza...'

class AddPhotoForm(forms.Form):
    # Following has to be called "picture" - and by extension have id of "id_picture"
    # Do not change, ON PAIN OF HUNTING CROSS-REFERENCES. You have been warned.
    picture = forms.ImageField(required=False)

@must_be_logged
def manage(request):
    if 'delete' in request.GET:
        try:
            ahid = AccountPhoto.objects.get(id=int(request.GET['delete']))  # throws Exception
        except:
            return HttpResponse(status=404)
        if ahid.account != request.user:
            return HttpResponse(status=403)
        ahid.delete()
        ranking_dirty()

    if request.method == 'POST':
        form = AddPhotoForm(request.POST, request.FILES)
        if form.is_valid():
              pic = upload_as(form.cleaned_data['picture'], RES_ACCOUNT_PHOTO)
              b = AccountPhoto(photo=pic, account=request.user)
              b.save()
              score_for(request.user, ACCOUNT_PHOTO_ADDED, b)
              accnews_for(request.user, RT_PRIVPHOTO_ADDED, b)
              del form
    try:
        form
    except:
        form = AddPhotoForm()

    return render('account/manage_gallery.html', request, form=form)


def ajax_push_comment(request, uphid):
    try:
        ph = AccountPhoto.objects.get(id=int(uphid))
    except:
        return Http404

    content = request.POST['content']

    request.session['suggested_user_photo'] = ph.id

    if content == DEFAULT_COMMENT_TEXT:
        return redirect('/profile/%s/gallery/' % (ph.account.id, ))

    try:
        lastcomm = AccountPhotoComment.objects.filter(photo=ph).filter(commentor=request.user)[0]
    except:
        pass
    else:
        if (datetime.now() - lastcomm.made_on) < timedelta(0, 15):
            # too soon, limit in effect
            request.session['err_comment_too_fast'] = True
            return redirect('/profile/%s/gallery/' % (ph.account.id, ))

    apc = AccountPhotoComment(photo=ph, content=content, commentor=request.user)
    apc.save()
    score_for(request.user, ACCOUNT_PHOTO_COMMENT_ADDED, apc)
    accnews_for(request.user, RT_COMMENT_PRIVGAL, ph)

    return redirect('/profile/%s/gallery/' % (ph.account.id, ))

def ajax_get_comments(request, uphid):
    try:
        ph = AccountPhoto.objects.get(id=int(uphid))
    except:
        raise Http404

    cs = """
        {% load photo %}
        <div class="box_header_title_fstyle">KOMENTARZE</div>            
        <div class="entries">
            {% for comment in comments %}
            <div class="entry">
                <div class="avatar"><a href="/profile/{{ comment.commentor.id }}/"><img src="{{ comment.account.avatar|path:"avatar:84,84" }}"></a></div>
                <div class="nick"><a href="/profile/{{ comment.commentor.id }}/">{{ comment.commentor.login }}</a></div>
                <div class="timestamp">{{ comment.made_on|date:"d.n.Y" }}</div>
                <div class="content">
                    {{ comment.content|linebreaksbr }}
                </div>
            </div>
            <div class="separator"></div>
            {% endfor %}
        </div>                
        {% if request != None %}
        <div id="odpowiedz_box">
            <div class="title">Odpowiedz</div>
            <form action="/bar/{{ bar.id }}/ajax/?op=comment" method="post" id="comment_form">
                <textarea name="content" onclick="if (this.value == '{{ default_comment_text }}') this.value=''">{{ default_comment_text }}</textarea>                       
                <button class="send" onclick="$('#comment_form').attr('action', '/profile/gallery/comment/'+curPhotoID+'/')[0].submit()"></button>
            </form>
        </div>
        {% else %}
            <div class="comment_needs_to_login">Musisz być zalogowany/a by pisać komentarze<br style="float: none;"><a href="/login/">ZALOGUJ SIĘ</a></div>
        {% endif %}
        """    
    template = Template(cs)

    return HttpResponse(template.render(Context({'request':request, 'comments': ph.comments.all()})))

@must_be_logged
def change_friend_status(request, uid):
    try:
        user = Account.objects.get(id=int(uid))
    except:
        return Http404

    if 'op' not in request.GET: return HttpResponse(status=401)
    if request.GET['op'] == 'befriend':
        try:
            gfef = request.user.get_familiar_entry_for(user)
        except:
            pass
        else:
            return HttpResponse(status=412) # Precondition failed

        user.invite_to_be_a_friend(request.user)
    elif request.GET['op'] == 'unfriend':
        try:
            user.unfriend(request.user)
        except:
            return HttpResponse(status=412) # Precondition failed
    
    return redirect('/profile/%s/gallery/' % (user.id, ))

def view_user_gallery(request, uid):
    try:
        user = Account.objects.get(id=int(uid))
    except:
        return Http404

    spdict = standard_profile_page_dict(request) if request.user != None else {}

    photos = list(user.photos.all())

    is_owner = user == request.user

    try:
        picked_photo = AccountPhoto.objects.get(id=request.session['suggested_user_photo'])
        if picked_photo.account != user: raise Exception
    except:
        try:
            picked_photo = photos[0]
        except:
            picked_photo = False


    if picked_photo in photos:
        photos.remove(picked_photo)
        photos = [picked_photo] + photos

    if 'err_comment_too_fast' in request.session:
        del request.session['err_comment_too_fast']
        err_comment_too_fast = True
    else:
        err_comment_too_fast = False   

    # ascertain friend status
    friend = None
    if request.user != None:
        if user.id != request.user.id:   # only here it makes sense
            for familiar in request.user.befriender_set.all():
                if familiar.befriendee == user:
                    # Found this entry!
                    friend = familiar.confirmed
                    familiar_entry = familiar
                    break
            if friend == None:
                for familiar in request.user.befriendee_set.all():
                    if familiar.befriender == user:
                        # Found this entry!
                        friend = familiar.confirmed
                        familiar_entry = familiar
                        break

    return render('account/view_user_gallery.html', request, user=user,
                                                             photos=photos,
                                                             err_comment_too_fast=err_comment_too_fast,
                                                             is_owner=is_owner,
                                                             is_friend=friend,
                                                             certainly_not_friend=friend == None,
                                                             default_comment_text=DEFAULT_COMMENT_TEXT,
                                                             picked_photo=picked_photo,
                                                             **spdict)