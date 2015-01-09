#########
App-Hooks
#########

With App-Hooks you can attach whole Django applications to pages. For example
you have a news app and you want it attached to your news page.

To create an apphook create a ``cms_app.py`` in your application. And in it
write the following::

    from cms.app_base import CMSApp
    from cms.apphook_pool import apphook_pool
    from django.utils.translation import ugettext_lazy as _

    class MyApphook(CMSApp):
        name = _("My Apphook")
        urls = ["myapp.urls"]

    apphook_pool.register(MyApphook)

Replace ``myapp.urls`` with the path to your applications ``urls.py``.

Now edit a page and open the advanced settings tab. Select your new apphook
under "Application". Save the page.

.. warning::

    Whenever you add or remove an apphook, change the slug of a page containing
    an apphook or the slug if a page which has a descendant with an apphook,
    you have to restart your server to re-load the URL caches.

.. note::

    If at some point you want to remove this apphook after deleting the cms_app.py
    there is a cms management command called uninstall apphooks
    that removes the specified apphook(s) from all pages by name.
    eg. ``manage.py cms uninstall apphooks MyApphook``.
    To find all names for uninstallable apphooks there is a command for this as well
    ``manage.py cms list apphooks``.

If you attached the app to a page with the url ``/hello/world/`` and the app has
a urls.py that looks like this::

    from django.conf.urls import *

    urlpatterns = patterns('sampleapp.views',
        url(r'^$', 'main_view', name='app_main'),
        url(r'^sublevel/$', 'sample_view', name='app_sublevel'),
    )

The ``main_view`` should now be available at ``/hello/world/`` and the
``sample_view`` has the url ``/hello/world/sublevel/``.


.. note::

    CMS pages **below** the page to which the apphook is attached to, **can** be visible,
    provided that the apphook urlconf regexps are not too greedy. From a URL resolution
    perspective, attaching an apphook works in same way than inserting the apphook urlconf
    in the root urlconf at the same path as the page is attached to.

.. note::

    All views that are attached like this must return a
    :class:`~django.template.RequestContext` instance instead of the
    default :class:`~django.template.Context` instance.


*************
Apphook Menus
*************

If you want to add a menu to that page as well that may represent some views
in your app add it to your apphook like this::

    from myapp.menu import MyAppMenu

    class MyApphook(CMSApp):
        name = _("My Apphook")
        urls = ["myapp.urls"]
        menus = [MyAppMenu]

    apphook_pool.register(MyApphook)


For an example if your app has a :class:`Category` model and you want this
category model to be displayed in the menu when you attach the app to a page.
We assume the following model::

    from django.db import models
    from django.core.urlresolvers import reverse
    import mptt

    class Category(models.Model):
        parent = models.ForeignKey('self', blank=True, null=True)
        name = models.CharField(max_length=20)

        def __unicode__(self):
            return self.name

        def get_absolute_url(self):
            return reverse('category_view', args=[self.pk])

    try:
        mptt.register(Category)
    except mptt.AlreadyRegistered:
        pass

We would now create a menu out of these categories::

    from menus.base import NavigationNode
    from menus.menu_pool import menu_pool
    from django.utils.translation import ugettext_lazy as _
    from cms.menu_bases import CMSAttachMenu
    from myapp.models import Category

    class CategoryMenu(CMSAttachMenu):

        name = _("test menu")

        def get_nodes(self, request):
            nodes = []
            for category in Category.objects.all().order_by("tree_id", "lft"):
                node = NavigationNode(
                    category.name,
                    category.get_absolute_url(),
                    category.pk,
                    category.parent_id
                )
                nodes.append(node)
            return nodes

    menu_pool.register_menu(CategoryMenu)

If you add this menu now to your app-hook::

    from myapp.menus import CategoryMenu

    class MyApphook(CMSApp):
        name = _("My Apphook")
        urls = ["myapp.urls"]
        menus = [MyAppMenu, CategoryMenu]

You get the static entries of :class:`MyAppMenu` and the dynamic entries of
:class:`CategoryMenu` both attached to the same page.

.. _multi_apphook:

***************************************
Attaching an Application multiple times
***************************************

If you want to attach an application multiple times to different pages you have 2 possibilities.

1. Give every application its own namespace in the advanced settings of a page.
2. Define an ``app_name`` attribute on the CMSApp class.

The problem is that if you only define a namespace you need to have multiple templates per attached app.

For example::

    {% url 'my_view' %}

Will not work anymore when you namespace an app. You will need to do something like::

    {% url 'my_namespace:my_view' %}

The problem is now if you attach apps to multiple pages your namespace will change.
The solution for this problem are application namespaces.

If you'd like to use application namespaces to reverse the URLs related to
your app, you can assign a value to the `app_name` attribute of your app
hook like this::

    class MyNamespacedApphook(CMSApp):
        name = _("My Namespaced Apphook")
        urls = ["myapp.urls"]
        app_name = "myapp_namespace"

    apphook_pool.register(MyNamespacedApphook)


.. note::
    If you do provide an ``app_label``, then you will need to also give the app
    a unique namespace in the advanced settings of the page. If you do not, and
    no other instance of the app exists using it, then the 'default instance
    namespace' will be automatically set for you. You can then either reverse
    for the namespace(to target different apps) or the app_name (to target
    links inside the same app).

If you use app namespace you will need to give all your view ``context`` a ``current_app``::

  def my_view(request):
      current_app = resolve(request.path_info).namespace
      context = RequestContext(request, current_app=current_app)
      return render_to_response("my_templace.html", context_instance=context)

.. note::
    You need to set the current_app explicitly in all your view contexts as django does not allow an other way of doing
    this.

You can reverse namespaced apps similarly and it "knows" in which app instance it is:

.. code-block:: html+django

    {% url myapp_namespace:app_main %}

If you want to access the same url but in a different language use the language
template tag:

.. code-block:: html+django

    {% load i18n %}
    {% language "de" %}
        {% url myapp_namespace:app_main %}
    {% endlanguage %}


.. note::

    The official Django documentation has more details about application and
    instance namespaces, the `current_app` scope and the reversing of such
    URLs. You can look it up at https://docs.djangoproject.com/en/dev/topics/http/urls/#url-namespaces

When using the `reverse` function, the `current_app` has to be explicitly passed
as an argument. You can do so by looking up the `current_app` attribute of
the request instance::

    def myviews(request):
        current_app = resolve(request.path_info).namespace

        reversed_url = reverse('myapp_namespace:app_main',
                current_app=current_app)
        ...

Or, if you are rendering a plugin, of the context instance::

    class MyPlugin(CMSPluginBase):
        def render(self, context, instance, placeholder):
            # ...
            current_app = resolve(request.path_info).namespace
            reversed_url = reverse('myapp_namespace:app_main',
                    current_app=current_app)
            # ...

.. _apphook_permissions:

*******************
Apphook Permissions
*******************

By default all apphooks have the same permissions set as the page they are assigned to.
So if you set login required on page the attached apphook and all it's urls have the same
requirements.

To disable this behavior set ``permissions = False`` on your apphook::

    class SampleApp(CMSApp):
        name = _("Sample App")
        urls = ["project.sampleapp.urls"]
        permissions = False



If you still want some of your views to have permission checks you can enable them via a decorator:

``cms.utils.decorators.cms_perms``

Here is a simple example::

    from cms.utils.decorators import cms_perms

    @cms_perms
    def my_view(request, **kw):
        ...


If you have your own permission check in your app, or just don't want to wrap some nested apps
with CMS permission decorator, then use ``exclude_permissions`` property of apphook::

    class SampleApp(CMSApp):
        name = _("Sample App")
        urls = ["project.sampleapp.urls"]
        permissions = True
        exclude_permissions = ["some_nested_app"]


For example, django-oscar_ apphook integration needs to be used with exclude permissions of dashboard app,
because it use `customizable access function`__. So, your apphook in this case will looks like this::

    class OscarApp(CMSApp):
        name = _("Oscar")
        urls = [
            patterns('', *application.urls[0])
        ]
        exclude_permissions = ['dashboard']

.. _django-oscar: https://github.com/tangentlabs/django-oscar
.. __: https://github.com/tangentlabs/django-oscar/blob/0.7.2/oscar/apps/dashboard/nav.py#L57

***********************************************
Automatically restart server on apphook changes
***********************************************

As mentioned above, whenever you add or remove an apphook, change the slug of a
page containing an apphook or the slug if a page which has a descendant with an
apphook, you have to restart your server to re-load the URL caches. To allow
you to automate this process, the django CMS provides a signal
:obj:`cms.signals.urls_need_reloading` which you can listen on to detect when
your server needs restarting. When you run ``manage.py runserver`` a restart
should not be needed.

.. warning::

    This signal does not actually do anything. To get automated server
    restarting you need to implement logic in your project that gets
    executed whenever this signal is fired. Because there are many ways of
    deploying Django applications, there is no way we can provide a generic
    solution for this problem that will always work.

.. warning::

    The signal is fired **after** a request. If you change something via API
    you need a request for the signal to fire.
