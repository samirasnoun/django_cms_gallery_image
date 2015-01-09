########################
Templates & Placeholders
########################

In this tutorial we'll introduce Placeholders, and we're also going to show how
you can make your own HTML templates CMS-ready.

Templates
#########

You can use HTML templates to customise the look of your website, define
Placeholders to mark sections for managed content and use special tags to
generate menus and more.

You can define multiple templates, with different layouts or built-in
components, and choose them for each page as required. A page's template
switched for another at any time.

You'll find the site's templates in ``mysite/templates``. If you didn't change
the automatically-created home page's template, it's ``feature.html``.

Placeholders
############

Placeholders are an easy way to define sections in an HTML template that will
be filled with content from the database when the page is rendered. This
content is edited using django CMS's frontend editing mechanism, using Django
templatetags.

You can see them in ``feature.html``: ``{% placeholder "feature" %}`` and ``{%
placeholder "content" %}``.

You'll also see ``{% load cms_tags %}`` in that file - ``cms_tags`` is the
required templatetag library.

If you're not already familiar with Django templatetags, you can find out more
in the `Django documentation
<https://docs.djangoproject.com/en/dev/topics/templates/>`_.

Try removing a placeholder from the template, or adding a new one in the
template's HTML structure.

Static Placeholders
*******************

The content of the placeholders we've encountered so far is different for
every page. Sometimes though you'll want to have a section on your website
which should be the same on every single page, such as a footer block.

You *could* hardcode your footer into the template, but it would be nicer to be
able to manage it through the CMS. This is what **static placeholders** are for.

Static placeholders are an easy way to display the same content on multiple
locations on your website. Static placeholders act almost like normal
placeholders, except for the fact that once a static placeholder is created and
you added content to it, it will be saved globally. Even when you remove the
static placeholders from a template, you can reuse them later.

So let's add a footer to all our pages. Since we want our footer on every
single page, we should add it to our base template
(``mysite/templates/base.html``). Place it at the bottom of the HTML body::

    <footer>
      {% static_placeholder 'footer' %}
    </footer>

Save the template and return to your browser. Change to ``Draft`` and then
``Structure`` mode and add some content to it.

After you've saved it, you'll see that it appears on your site's other pages
too.

Rendering Menus
---------------

In order to render the CMS's menu in your template you can use the :doc:`show_menu </reference/navigation>` tag.

The example we use in ``mysite/templates/base.html``  is::

    <ul class="nav navbar-nav">
        {% show_menu 0 1 100 100 "menu.html" %}
    </ul>

Any template that uses ``show_menu`` must load the CMS's ``menu_tags`` library
first::

    {% load menu_tags %}


If you chose "bootstrap" while setting up with djangocms-installer, the menu
will already be there and ``templates/menu.html`` will already contain a
version that uses bootstrap compatible markup.

Next we'll look at django CMS plugins.
