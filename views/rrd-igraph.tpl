<img class="rrdli-graph" src="{{url}}">

<script type="text/javascript" src="//code.jquery.com/jquery-2.0.3.min.js"></script>
<script type="text/javascript" src="//code.jquery.com/ui/1.10.3/jquery-ui.min.js"></script>
<script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/jquery-mousewheel/3.1.6/jquery.mousewheel.js"></script>
<script type="text/javascript" src="{{get_url('static', file='lib/jquery-zoomly/zoomy.js')}}"></script>

<script type="text/javascript">
    $( document ).ready(function() {
        $('.smoke-graph').zoomy({});
        $('.rrdli-graph').zoomy({connector:'rrdli'});
    });
</script>
